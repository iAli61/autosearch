from typing import Dict, Any, Callable, get_type_hints
from inspect import signature
from autosearch.project_config import ProjectConfig


class BaseFunction:
    """
    A base class for functions to be used with agents.
    """

    def __init__(self, name: str, description: str, func: Callable, project_config: ProjectConfig):
        """
        Initialize the BaseFunction.

        Args:
            name (str): The name of the function.
            description (str): A description of what the function does.
            func (Callable): The actual function to be called.
            project_config (ProjectConfig): The project configuration.
        """
        self.name = name
        self.description = description
        self._original_func = func
        self.project_config = project_config
        self.func = self._create_wrapper()

    def _create_wrapper(self) -> Callable:
        """
        Create a wrapper function that automatically injects project_config
        and preserves Annotated types.
        """
        def wrapper(*args, **kwargs):
            sig = signature(self._original_func)
            bound_args = sig.bind_partial(*args, **kwargs)
            if 'project_config' in sig.parameters:
                bound_args.arguments['project_config'] = self.project_config
            return self._original_func(*bound_args.args, **bound_args.kwargs)

        # Get the original function's signature
        orig_sig = signature(self._original_func)
        
        # Create a new signature for the wrapper, excluding 'project_config'
        new_params = [
            param for name, param in orig_sig.parameters.items()
            if name != 'project_config'
        ]
        wrapper.__signature__ = orig_sig.replace(parameters=new_params)

        # Preserve Annotated types
        orig_annotations = get_type_hints(self._original_func, include_extras=True)
        wrapper.__annotations__ = {
            k: v for k, v in orig_annotations.items()
            if k != 'project_config'
        }

        return wrapper

    def get_function_details(self) -> Dict[str, Any]:
        """
        Get the function details.

        Returns:
            Dict[str, Any]: A dictionary containing the function name, description, and callable.
        """
        return {
            "name": self.name,
            "description": self.description,
            "func": self.func
        }