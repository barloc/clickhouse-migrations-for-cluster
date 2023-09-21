class CHMFCBaseError(Exception):
    "Base error for chmfc service"
    pass


class CHMFCIdenticalVersionError(Exception):
    def __init__(self, filenames: []):
        message = f"Migration files with identical versions: {','.join(filenames)}"
        super().__init__(message)

class CHMFCMigrationsDirectoryEmptyError(Exception):
    def __init__(self, mig_path: str):
        message = f"Migrations directory is empty: {mig_path}"
        super().__init__(message)
