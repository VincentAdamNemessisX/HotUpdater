import ast
import importlib
import os
import sys
import time
import types
from collections import deque, defaultdict
from typing import Optional


def safe_file_read(filepath: str) -> str:
    """多编码策略文件读取"""
    encodings = ['utf-8', 'gbk', 'latin-1']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, IOError):
            continue
    raise UnicodeDecodeError("", "", "", "", f"无法解码文件: {filepath}")


class EnhancedDependencyTracker:
    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)
        self.dep_graph = defaultdict(set)
        self.reverse_graph = defaultdict(set)
        self._module_cache = {}

    def _is_project_module(self, module: types.ModuleType) -> bool:
        """改进的项目模块判断"""
        if not hasattr(module, '__file__'):
            return False

        filepath = os.path.abspath(module.__file__)
        return (
                filepath.startswith(self.project_root) and
                not self._is_standard_lib(filepath)
        )

    @staticmethod
    def _is_standard_lib(path: str) -> bool:
        """判断是否标准库模块"""
        return any(
            path.startswith(sys.prefix + os.sep + lib_dir)
            for lib_dir in ['lib', 'Lib']
        )

    @staticmethod
    def _resolve_absolute_name(current: str, target: Optional[str], level: int) -> str:
        """增强相对导入解析"""
        if level == 0:
            return target or ''

        parts = current.split('.')
        required_depth = level - 1
        if len(parts) <= required_depth:
            raise ImportError(f"相对导入层级错误: {current} level={level}")

        base = '.'.join(parts[:-required_depth])
        return f"{base}.{target}" if target else base

    @staticmethod
    def _process_import_alias(alias: ast.alias) -> str:
        """处理导入别名"""
        if alias.asname:
            return alias.name.split('.')[0]
        return alias.name

    def build_dependencies(self):
        """重构依赖构建逻辑"""
        self.dep_graph.clear()
        self.reverse_graph.clear()

        for mod_name, module in list(sys.modules.items()):
            if not self._is_project_module(module):
                continue

            try:
                filepath = getattr(module, '__file__', '').replace('.pyc', '.py')
                if not os.path.exists(filepath):
                    continue

                code = safe_file_read(filepath)
                tree = ast.parse(code)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            parent = self._process_import_alias(alias)
                            self._add_dependency(mod_name, parent)

                    elif isinstance(node, ast.ImportFrom):
                        parent = self._resolve_absolute_name(
                            current=mod_name,
                            target=node.module,
                            level=node.level or 0
                        )
                        self._add_dependency(mod_name, parent)

            except Exception as e:
                print(f"🔧 模块分析异常 [{mod_name}]: {str(e)}")

    def _add_dependency(self, child: str, parent: str):
        """强化依赖关系校验"""
        if not parent or parent == child:
            return

        parent = parent.split('.')[0]  # 处理多级导入
        parent = parent.lstrip('.')

        if parent not in sys.modules:
            return

        if not self._is_project_module(sys.modules[parent]):
            return

        self.dep_graph[child].add(parent)
        self.reverse_graph[parent].add(child)


class SmartFileWatcher:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.file_states = {}
        self._init_watcher()

    def _init_watcher(self):
        """初始化文件状态快照"""
        for root, _, files in os.walk(self.project_root):
            for f in files:
                if f.endswith('.py'):
                    path = os.path.join(root, f)
                    self.file_states[path] = self._get_file_signature(path)

    @staticmethod
    def _get_file_signature(path: str) -> tuple:
        """获取文件特征签名"""
        stat = os.stat(path)
        return stat.st_mtime, stat.st_size, stat.st_ino

    def detect_changes(self) -> set:
        """改进型变化检测"""
        changed = set()

        # 检测现有文件变化
        for path in list(self.file_states.keys()):
            if not os.path.exists(path):
                del self.file_states[path]
                changed.add(self._path_to_modname(path))
                continue

            new_sig = self._get_file_signature(path)
            if new_sig != self.file_states[path]:
                self.file_states[path] = new_sig
                changed.add(self._path_to_modname(path))

                # 检测新增文件
        for root, _, files in os.walk(self.project_root):
            for f in files:
                if f.endswith('.py'):
                    path = os.path.join(root, f)
                    if path not in self.file_states:
                        self.file_states[path] = self._get_file_signature(path)
                        changed.add(self._path_to_modname(path))

        return changed

    def _path_to_modname(self, path: str) -> str:
        """文件路径转模块名"""
        rel_path = os.path.relpath(path, self.project_root)
        return rel_path.replace(os.sep, '.').replace('.py', '')


class AdvancedHotReloader:
    def __init__(self, project_root: str):
        self.tracker = EnhancedDependencyTracker(project_root)
        self.watcher = SmartFileWatcher(project_root)
        self.tracker.build_dependencies()

        # 运行时状态缓存
        self.class_registry = defaultdict(list)
        self.function_registry = defaultdict(set)

    def topological_sort(self, modules: set) -> list:
        """改进拓扑排序算法"""
        in_degree = defaultdict(int)
        graph = self.tracker.dep_graph

        # 初始化入度表
        for module in modules:
            for dep in graph.get(module, []):
                if dep in modules:
                    in_degree[module] += 1

                    # Kahn算法实现
        queue = deque([m for m in modules if in_degree[m] == 0])
        order = []

        while queue:
            node = queue.popleft()
            order.append(node)

            for neighbor in self.tracker.reverse_graph.get(node, []):
                if neighbor not in modules:
                    continue
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(modules):
            print("⚠️ 检测到循环依赖，建议手动处理")
            return list(modules)  # 降级处理

        return order

    def deep_update(self, module: types.ModuleType):
        """增强型深度更新"""
        # 类实例更新
        for name in dir(module):
            new_obj = getattr(module, name)
            old_obj = globals().get(name, None)

            if isinstance(new_obj, type) and old_obj:
                for detail_instance in self.class_registry.get(old_obj, set()):
                    detail_instance.__class__ = new_obj

                    # 更新类引用
                self.class_registry[new_obj] = self.class_registry.pop(old_obj, set())

        # 函数更新
        for name in dir(module):
            new_func = getattr(module, name)
            if isinstance(new_func, types.FunctionType):
                old_func = globals().get(name)
                if old_func and old_func.__code__ != new_func.__code__:
                    for callback in self.function_registry.get(old_func, set()):
                        callback.__code__ = new_func.__code__

                    self.function_registry[new_func] = self.function_registry.pop(old_func, set())

    def run(self, interval: float = 1.0):
        """主运行循环"""
        while True:
            changed = self.watcher.detect_changes()
            if changed:
                print(f"🔄 检测到变更模块: {', '.join(changed)}")
                self._process_changes(changed)
            time.sleep(interval)

    def _process_changes(self, changed_modules: set):
        """变更处理流程"""
        try:
            # 重建依赖关系
            self.tracker.build_dependencies()

            # 计算影响范围
            affected = set(changed_modules)
            queue = deque(changed_modules)
            while queue:
                mod = queue.popleft()
                for dependent in self.tracker.reverse_graph.get(mod, []):
                    if dependent not in affected:
                        affected.add(dependent)
                        queue.append(dependent)

                        # 生成重载顺序
            reload_order = self.topological_sort(affected)
            print(f"📦 重载顺序: {' → '.join(reload_order)}")

            # 执行重载
            for mod_name in reload_order:
                if mod_name not in sys.modules:
                    continue

                try:
                    module = importlib.reload(sys.modules[mod_name])
                    self.deep_update(module)
                    print(f"✅ 成功重载: {mod_name}")
                    # 新增逻辑：自动执行最新run方法
                    for cls in self.class_registry.keys():
                        for obj in self.class_registry[cls]:
                            if hasattr(obj, 'run'):
                                obj.run()
                except Exception as e:
                    print(f"❌ 重载失败 [{mod_name}]: {str(e)}")
                    # 失败后重建依赖关系
                    self.tracker.build_dependencies()

        except Exception as e:
            print(f"🔥 系统级错误: {str(e)}")
            import traceback
            traceback.print_exc()
