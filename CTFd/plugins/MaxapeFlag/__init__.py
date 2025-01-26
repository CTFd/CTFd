
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.flags import BaseFlag,FlagException,FLAG_CLASSES


class CTFdMAXAPEFlag(BaseFlag):
    name = "maxape"
    templates = {
        "create": "/plugins/MaxapeFlag/assets/create.html",
        "update": "/plugins/MaxapeFlag/assets/edit.html",
    }

    @staticmethod
    def compare(chal_key_obj, provided):
        saved = chal_key_obj.content
        data = chal_key_obj.data
        try:
            provided_np = [float(x) for x in provided.split(",")]
            saved_np = [float(x) for x in saved.split(",")]
        except ValueError:
            raise FlagException("Flag must be comma separated floats")
        if len(provided_np) != len(saved_np):
            raise FlagException(f"Incorrect number of values: provided {len(provided_np)}, expected {len(saved_np)}")
        flag = True
        for p,s in zip(provided_np, saved_np):
            mape = abs(p-s)/s
            mape *= 100
            if mape > float(data):
                flag = False
        return flag



def load(app):
    FLAG_CLASSES['maxape'] = CTFdMAXAPEFlag
    register_plugin_assets_directory(app, base_path="/plugins/MaxapeFlag/assets/")
    