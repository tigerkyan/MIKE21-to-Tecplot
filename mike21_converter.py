#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIKE21 to Tecplot 转换器
主程序类，提供完整的转换功能

作者: GitHub Copilot
版本: 2.2 - 添加线程池并行处理支持
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import numpy as np
import mikeio
from shapely.geometry import Point, Polygon, LineString
import ezdxf
# 使用线程池替代进程池，避免PyInstaller环境问题
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml
import os
import threading


class MIKE21Converter:
    """MIKE21 DFSU 文件到 Tecplot 格式转换器"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化转换器

        Args:
            config_path: 配置文件路径，默认为 config.yaml
        """
        self.config_path = config_path or "config.yaml"
        self.config = self._load_config()
        self._setup_logging()
        self.logger = logging.getLogger(__name__)

    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件 {self.config_path} 未找到")
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")

    def _setup_logging(self):
        """设置日志记录"""
        log_level = logging.INFO if self.config.get('processing', {}).get('verbose', True) else logging.WARNING
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('mike21_converter.log', encoding='utf-8')
            ]
        )

    def load_closed_polyline(self, dxf_path: Path) -> Polygon:
        """从DXF文件加载闭合多段线"""
        try:
            doc = ezdxf.readfile(dxf_path)
            pl = next((e for e in doc.modelspace().query("LWPOLYLINE") if e.closed), None)
            if pl is None:
                raise ValueError("DXF 中找不到闭合多段线！请确认已执行 C 闭合。")
            coords = [(x, y) for x, y, *_ in pl.get_points("xy")]
            return Polygon(coords)
        except Exception as e:
            self.logger.error(f"加载DXF文件 {dxf_path} 失败: {e}")
            raise

    def load_axis_polyline(self, dxf_path: Path) -> LineString:
        """从DXF文件加载轴线"""
        try:
            doc = ezdxf.readfile(dxf_path)
            line = next((e for e in doc.modelspace().query("LWPOLYLINE")), None)
            if line is None:
                raise ValueError("DXF 中找不到多段线")
            coords = [(x, y) for x, y, *_ in line.get_points("xy")]
            return LineString(coords)
        except Exception as e:
            self.logger.error(f"加载轴线文件 {dxf_path} 失败: {e}")
            raise

    def project_uv_along_axis(self, elem_xy: np.ndarray, u: np.ndarray,
                             v: np.ndarray, axis: LineString) -> Tuple[np.ndarray, np.ndarray]:
        """将速度矢量投影到轴线坐标系"""
        vx, vy = [], []
        for xyz, uu, vv in zip(elem_xy, u, v):
            x, y = xyz[:2]
            pt = Point(x, y)
            proj = axis.project(pt)
            axis_pt = axis.interpolate(proj)
            tangent = np.array(axis.interpolate(proj + 1e-6).coords[0]) - np.array(axis_pt.coords[0])
            if np.linalg.norm(tangent) == 0:
                tangent = np.array([1.0, 0.0])
            else:
                tangent = tangent / np.linalg.norm(tangent)
            normal = np.array([-tangent[1], tangent[0]])
            vel_vec = np.array([uu, vv])
            vx.append(np.dot(vel_vec, tangent))
            vy.append(np.dot(vel_vec, normal))
        return np.array(vx), np.array(vy)

    def write_tecplot_elements(self, out_path: Path, elem_xy: np.ndarray,
                              variables: np.ndarray, title: str = "MIKE21 Data"):
        """输出单元中心数据到Tecplot格式"""
        precision = self.config.get('output_settings', {}).get('precision', 6)
        variables = np.nan_to_num(variables, nan=0.0)

        with open(out_path, "w", encoding='utf-8') as f:
            f.write(f'TITLE = "{title}"\n')
            var_names = ["X", "Y", "u", "v", "w", "velocity"]
            if variables.shape[1] > 6:
                var_names.extend(["Vx", "Vy"])
            f.write('VARIABLES = ' + ', '.join(f'"{v}"' for v in var_names) + '\n')
            f.write(f'ZONE I={len(elem_xy)}, DATAPACKING=POINT\n')
            for row in variables:
                f.write(" ".join(f"{v:.{precision}f}" for v in row) + "\n")

    def write_tecplot_nodes(self, out_path: Path, node_xy: np.ndarray,
                           conn_reindex: np.ndarray, variables: np.ndarray,
                           title: str = "MIKE21 Data"):
        """输出节点数据到Tecplot格式"""
        precision = self.config.get('output_settings', {}).get('precision', 6)
        variables = np.nan_to_num(variables, nan=0.0)

        with open(out_path, "w", encoding='utf-8') as f:
            f.write(f'TITLE = "{title}"\n')
            var_names = ["X", "Y", "u", "v", "w", "velocity"]
            if variables.shape[1] > 6:
                var_names.extend(["Vx", "Vy"])
            f.write('VARIABLES = ' + ', '.join(f'"{v}"' for v in var_names) + '\n')
            f.write(f'ZONE N={len(node_xy)}, E={len(conn_reindex)}, F=FEPOINT, ET=TRIANGLE\n')
            for row in variables:
                f.write(" ".join(f"{v:.{precision}f}" for v in row) + "\n")
            for tri in conn_reindex:
                f.write(f"{tri[0]+1} {tri[1]+1} {tri[2]+1}\n")

    def process_full_field(self, ds, dfsu_path: Path, out_dir: Path) -> bool:
        """处理全场数据输出"""
        if not self.config.get('output_settings', {}).get('export_full_field', True):
            return False

        try:
            # 读取速度数据
            u = ds["U velocity"].values
            v = ds["V velocity"].values
            w = ds["W velocity"].values if "W velocity" in ds.items else np.zeros_like(u)
            velocity = np.sqrt(u**2 + v**2 + w**2)

            # 获取几何信息
            node_xy_all = np.array(ds.geometry.node_coordinates)
            elem_xy = np.array(ds.geometry.element_coordinates)
            elem_tab = np.array([np.array(e, dtype=int) for e in ds.geometry.element_table if len(e) == 3])

            # 坐标变换参数
            x_shift = self.config.get('coordinate_transform', {}).get('x_shift', 0)
            y_shift = self.config.get('coordinate_transform', {}).get('y_shift', 0)

            if u.shape[0] == elem_xy.shape[0]:
                # 单元中心数据
                out_all = out_dir / f"{dfsu_path.stem}_allfield.dat"
                elem_xy_out = elem_xy.copy()
                elem_xy_out[:, 0] -= x_shift
                elem_xy_out[:, 1] -= y_shift
                vars_all = np.column_stack([elem_xy_out[:, 0], elem_xy_out[:, 1], u, v, w, velocity])
                self.write_tecplot_elements(out_all, elem_xy_out, vars_all,
                                          "MIKE21 全场流速矢量(单元中心)")
                self.logger.info(f"✅ 全场输出(单元中心): {out_all.name}, 数据点数: {len(elem_xy_out)}")

            elif u.shape[0] == node_xy_all.shape[0]:
                # 节点数据
                out_all = out_dir / f"{dfsu_path.stem}_allfield.dat"
                node_xy_all_out = node_xy_all.copy()
                node_xy_all_out[:, 0] -= x_shift
                node_xy_all_out[:, 1] -= y_shift
                vars_all = np.column_stack([node_xy_all_out[:, 0], node_xy_all_out[:, 1], u, v, w, velocity])
                self.write_tecplot_nodes(out_all, node_xy_all_out, elem_tab, vars_all,
                                       "MIKE21 全场流速矢量(节点)")
                self.logger.info(f"✅ 全场输出(节点): {out_all.name}, 节点数: {len(node_xy_all_out)}, 单元数: {len(elem_tab)}")
            else:
                raise ValueError(f"数据维度不匹配: 节点数{node_xy_all.shape[0]}, 单元数{elem_xy.shape[0]}, 速度场长度{u.shape[0]}")

            return True

        except Exception as e:
            self.logger.error(f"全场处理失败: {e}")
            return False

    def process_regions(self, ds, dfsu_path: Path, out_dir: Path) -> Dict[str, bool]:
        """处理区域数据输出"""
        if not self.config.get('output_settings', {}).get('export_regions', True):
            return {}

        results = {}
        regions = self.config.get('regions', {})

        # 读取数据
        u = ds["U velocity"].values
        v = ds["V velocity"].values
        w = ds["W velocity"].values if "W velocity" in ds.items else np.zeros_like(u)
        velocity = np.sqrt(u**2 + v**2 + w**2)

        node_xy_all = np.array(ds.geometry.node_coordinates)
        elem_xy = np.array(ds.geometry.element_coordinates)
        elem_tab = np.array([np.array(e, dtype=int) for e in ds.geometry.element_table if len(e) == 3])

        x_shift = self.config.get('coordinate_transform', {}).get('x_shift', 0)
        y_shift = self.config.get('coordinate_transform', {}).get('y_shift', 0)

        for name, region_config in regions.items():
            try:
                # 加载区域和轴线
                region_poly = self.load_closed_polyline(Path(region_config["region_dxf"]))
                axis_line = self.load_axis_polyline(Path(region_config["axis_dxf"]))

                # 筛选区域内的单元
                mask_elem = np.array([region_poly.contains(Point(xy[0], xy[1])) for xy in elem_xy])
                if not mask_elem.any():
                    self.logger.warning(f"⚠️ 区域 {name} 在 {dfsu_path.name} 中无元素，已跳过该区域。")
                    results[name] = False
                    continue

                # 提取区域数据
                u_r = u[mask_elem]
                v_r = v[mask_elem]
                w_r = w[mask_elem]
                vel_r = velocity[mask_elem]
                elem_tab_r = elem_tab[mask_elem]
                elem_xy_r = elem_xy[mask_elem]

                # 投影到轴线坐标系
                vx_r, vy_r = self.project_uv_along_axis(elem_xy_r, u_r, v_r, axis_line)

                # 重建连接表
                nodes_keep = np.unique(elem_tab_r)
                node_map = {old: new for new, old in enumerate(nodes_keep)}
                conn_reindex = np.vectorize(node_map.get)(elem_tab_r)
                node_xy = node_xy_all[nodes_keep]

                # 构建输出变量
                vars_region = []
                for i in range(len(node_xy)):
                    xi, yi = node_xy[i][:2]
                    xi -= x_shift
                    yi -= y_shift
                    idx_match = np.any(elem_tab_r == nodes_keep[i], axis=1)
                    u_m = u_r[idx_match].mean()
                    v_m = v_r[idx_match].mean()
                    w_m = w_r[idx_match].mean()
                    vel_m = vel_r[idx_match].mean()
                    vx_m = vx_r[idx_match].mean()
                    vy_m = vy_r[idx_match].mean()
                    vars_region.append([xi, yi, u_m, v_m, w_m, vel_m, vx_m, vy_m])

                # 输出文件
                out_region = out_dir / f"{dfsu_path.stem}_{name}.dat"
                description = region_config.get('description', name)
                self.write_tecplot_nodes(out_region, node_xy, conn_reindex,
                                       np.array(vars_region), f"MIKE21 区域: {description}")
                self.logger.info(f"✅ 区域 {name} 输出: {out_region.name}")
                results[name] = True

            except Exception as e:
                self.logger.error(f"❌ 区域 {name} 处理失败: {e}")
                results[name] = False

        return results

    def process_single_file(self, dfsu_path: Path) -> Dict:
        """处理单个DFSU文件"""
        self.logger.info(f"📂 处理文件: {dfsu_path.name}")

        # 创建输出目录
        output_dir = Path(self.config['paths']['output_dir'])
        out_dir = output_dir / dfsu_path.stem
        out_dir.mkdir(parents=True, exist_ok=True)

        try:
            # 读取DFSU文件
            dfs = mikeio.open(dfsu_path)
            time_index = self.config.get('time_settings', {}).get('time_index')

            if time_index is None:
                ds = dfs.read()
            else:
                ds = dfs.read(time=[time_index])
                if ds.n_timesteps == 1:
                    ds = ds.isel(time=0)

            # 处理全场和区域数据
            full_field_success = self.process_full_field(ds, dfsu_path, out_dir)
            region_results = self.process_regions(ds, dfsu_path, out_dir)

            self.logger.info(f"✅ 完成: {dfsu_path.name}")

            return {
                'file': dfsu_path.name,
                'success': True,
                'full_field': full_field_success,
                'regions': region_results
            }

        except Exception as e:
            self.logger.error(f"❌ 处理 {dfsu_path.name} 时出错: {e}")
            return {
                'file': dfsu_path.name,
                'success': False,
                'error': str(e)
            }

    def run(self, input_files: Optional[List[str]] = None) -> Dict:
        """运行转换器 - 支持线程池并行处理"""
        # 确定输入文件
        if input_files:
            dfsu_files = [Path(f) for f in input_files if Path(f).exists()]
        else:
            input_dir = Path(self.config['paths']['input_dir'])
            dfsu_files = list(input_dir.glob("*.dfsu"))

        if not dfsu_files:
            self.logger.error("未找到任何DFSU文件！")
            return {'success': False, 'message': '未找到任何DFSU文件'}

        # 确保输出目录存在
        output_dir = Path(self.config['paths']['output_dir'])
        output_dir.mkdir(exist_ok=True)

        # 并行处理配置
        max_workers = self.config.get('processing', {}).get('parallel_workers')
        if max_workers is None:
            max_workers = min(len(dfsu_files), os.cpu_count() or 1)

        # 在PyInstaller环境中使用线程池而不是进程池
        use_parallel = self.config.get('processing', {}).get('enable_parallel', True)

        # 如果只有一个文件或配置为禁用并行处理，则使用单线程
        if len(dfsu_files) == 1 or max_workers == 1 or not use_parallel:
            self.logger.info(f"开始处理 {len(dfsu_files)} 个文件（单线程模式）")
            results = []
            for dfsu in dfsu_files:
                results.append(self.process_single_file(dfsu))
        else:
            # 使用线程池并行处理多个文件
            self.logger.info(f"开始处理 {len(dfsu_files)} 个文件，使用 {max_workers} 个线程")
            results = []

            # 创建线程锁来保护日志输出
            log_lock = threading.Lock()

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                future_to_file = {
                    executor.submit(self._process_file_with_lock, dfsu, log_lock): dfsu
                    for dfsu in dfsu_files
                }

                # 收集结果
                for future in as_completed(future_to_file):
                    try:
                        result = future.result()
                        results.append(result)

                        # 安全地输出进度信息
                        with log_lock:
                            if result['success']:
                                self.logger.info(f"🎯 完成文件: {result['file']}")
                            else:
                                self.logger.error(f"❌ 失败文件: {result['file']}")

                    except Exception as e:
                        file_path = future_to_file[future]
                        with log_lock:
                            self.logger.error(f"❌ 线程处理 {file_path.name} 时出错: {e}")
                        results.append({
                            'file': file_path.name,
                            'success': False,
                            'error': str(e)
                        })

        # 汇总结果
        successful = sum(1 for r in results if r['success'])
        processing_mode = "并行" if len(dfsu_files) > 1 and max_workers > 1 and use_parallel else "单线程"
        self.logger.info(f"处理完成（{processing_mode}模式）: {successful}/{len(dfsu_files)} 个文件成功")

        return {
            'success': True,
            'total_files': len(dfsu_files),
            'successful_files': successful,
            'processing_mode': processing_mode,
            'max_workers': max_workers if processing_mode == "并行" else 1,
            'results': results
        }

    def _process_file_with_lock(self, dfsu_path: Path, log_lock: threading.Lock) -> Dict:
        """带线程锁的文件处理方法，确保日志输出的线程安全"""
        try:
            # 在开始处理时安全地输出日志
            with log_lock:
                self.logger.info(f"🚀 开始处理: {dfsu_path.name} [线程: {threading.current_thread().name}]")

            # 调用原始的处理方法
            return self.process_single_file(dfsu_path)

        except Exception as e:
            with log_lock:
                self.logger.error(f"❌ 文件处理异常 {dfsu_path.name}: {e}")
            return {
                'file': dfsu_path.name,
                'success': False,
                'error': str(e)
            }
def main():
    """主函数"""
    try:
        converter = MIKE21Converter()
        result = converter.run()

        if result['success']:
            print(f"\n转换完成！成功处理 {result['successful_files']}/{result['total_files']} 个文件")
        else:
            print(f"\n转换失败：{result.get('message', '未知错误')}")

    except Exception as e:
        print(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()