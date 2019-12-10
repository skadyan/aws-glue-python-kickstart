import moto  # noqa

from osiris.base.logutils import get_logger

get_logger(__name__).info(f"Activating boto - {moto.__version__} -"
                          f" A library that allows you to easily mock out tests based on AWS infrastructure.")
