import os
import stat

from thumbtack_client import logger


class MountedDiskImageVolume(object):
    """An object that represents a single volume of a mounted disk image. For more information
        see `imagemounter.Volume <https://imagemounter.readthedocs.io/en/latest/python.html#imagemounter.Volume>`_ documentation.
        This class creates a Python object with its attributes set from the JSON-serialized dictionary passed in.

        Attributes
        ----------
        fsdescription : str
            Can be set to: 'logical volume', 'luks volume', 'bde volume', 'raid volume',
            'primary volume', 'basic data partition', or 'vss store' based on the fstype detected.
        fstype : str
            The file system type determined by `imagemounter.ImageParser.volume.determine_fs_type() <https://imagemounter.readthedocs.io/en/latest/python.html#imagemounter.Volume.determine_fs_type>`_
        index : int
            The volume index within its volume system.
        label : str
            The volume label determined by imagemounter.ImageParser.volume.init when it calls `load_fsstat_data() <https://imagemounter.readthedocs.io/en/latest/python.html#imagemounter.Volume.init>`_
        mountpoint : str
            The absolute path to the mounted disk image volume directory.
        offset : int
            The offset of the volume in the disk in bytes
        size : int
            The size of the volume in bytes.
        """
    def __init__(self, mounted_volume_obj):
        """Create a MountedDiskImageVolume object.

        Parameters
        ----------
        mounted_volume_obj : dict
            This dictionary should be refactored into its individual components.
            It is defined in the resources.py file as `volume_fields`.
        """
        self.fsdescription = mounted_volume_obj['fsdescription']
        self.fstype = mounted_volume_obj['fstype']
        self.index = mounted_volume_obj['index']
        self.label = mounted_volume_obj['label']
        self.mountpoint = mounted_volume_obj['mountpoint']
        self.offset = mounted_volume_obj['offset']
        self.size = mounted_volume_obj['size']

    def walk(self, file_filter=None):
        """Walks through every file in a given mountpoint directory.

        Parameters
        ----------
        file_filter : callable, optional
            A callable that accepts `mounted_file_path_on_disk` and returns a boolean
            of whether to yield that file.  For example, you can call
            `volume.walk(lambda x: x.endswith(".exe"))` to find all of the files
            with the `.exe` extension.

        Yields
        ------
        tuple (str, str)
            A tuple that contains (absolute path, path in volume)

        Examples
        --------
        >>> volume = MountedDiskImageVolume(mounted_volume_obj)
        >>> for (mounted_file_path_on_disk, file_path_within_volume) in volume.walk():
        ...     # Open the file and fetch the data.
        ...     with open(mounted_file_path_on_disk) as f:
        ...         data = f.read()
        ...
        ...     # Pass the full file path to a subprocess
        ...     md5hash = subprocess.check_output(['md5sum', mounted_file_path_on_disk])
        ...
        ...     # print file path as it appears in the volume
        ...     print(file_path_within_volume)
        """
        for dirpath, _, filenames in os.walk(self.mountpoint):
            for f in filenames:
                full_path = os.path.join(dirpath, f)
                if file_filter is None or file_filter(full_path):
                    # remove mounted prefix; eg '/tmp/thumbtack/im_x30_s3s'
                    path_within_volume = os.path.join(*full_path.split(os.path.sep)[4:])
                    yield (full_path, path_within_volume)

    def safe_walk(self, file_filter=None):
        """Walks through every file in a given mountpoint directory, skipping broken files.

        This is the preferred method over :meth:`~thumbtack.resources.MountedDiskImageVolume.walk()`
        since there are more checks to ensure that files are accessible. It skips broken
        symlinks, files that can't be read, and named pipes.

        Parameters
        ----------
        file_filter : callable, optional
            A callable that accepts `mounted_file_path_on_disk` and returns a boolean
            of whether to yield that file.  For example, you can call
            `volume.walk(lambda x: x.endswith(".exe"))` to find all of the files
            with the `.exe` extension.

        Yields
        ------
        tuple (str, str)
            A tuple that contains (absolute path, path in volume)
        """
        for full_path, path_within_volume in self.walk(file_filter):
            skip_file = False
            msg = None

            # Check for broken symlinks, observed on mounted NTFS reparse points
            if not os.path.exists(full_path):
                skip_file = True
                msg = 'Path does not exist (broken symlink?)'

            # Check for files that can't be read
            if not skip_file and not os.access(full_path, os.R_OK):
                skip_file = True
                msg = 'File not accessible for reading'

            # Ensure is regular file. Avoids named pipes, among other things
            if not skip_file and not stat.S_ISREG(os.stat(full_path).st_mode):
                skip_file = True
                msg = 'File is not a regular file'

            if skip_file:
                logger.info('Not processing mounted file "{}": {}'.format(full_path, msg))
                continue

            yield (full_path, path_within_volume)
