from thumbtack_client.MountedDiskImageVolume import MountedDiskImageVolume


class MountedDiskImage(object):
    """
        An object that represents a mounted disk image. This class creates a Python object with its
        attributes set from the JSON-serialized dictionary passed in.

        Attributes
        ----------
        mountpoint : str
            The absolute path to the mounted disk image directory.
        name : str
            Uses python's `os.path.split <https://docs.python.org/2/library/os.path.html>`_ to name the MountedDiskImage
            using the tail of the file path.
        volumes : list thumbtack.resources.MountedDiskImageVolume
            This is a list of each MountedDiskImageVolume object in the specified disk image.
        mounted_volumes : list thumbtack.resources.MountedDiskImageVolume
            This is a list of the MountedDiskImageVolume objects with a valid mountpoint.
        """
    def __init__(self, mounted_disk_obj):
        """Create a MountedDiskImage object.

        Parameters
        ----------
        mounted_disk_obj : dict
            This dictionary should be refactored into its individual components.
            It is defined in the resources.py file as `disk_fields`.
        """
        self.mountpoint = mounted_disk_obj['mountpoint']
        self.name = mounted_disk_obj['name']
        self.volumes = [MountedDiskImageVolume(v) for v in mounted_disk_obj['volumes']]
        self.mounted_volumes = [v for v in self.volumes if v.mountpoint]  # only volumes with a non-empty mountpoint
