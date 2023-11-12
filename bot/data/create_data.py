import models

models.Base.metadata.drop_all(models.engine)
models.Base.metadata.create_all(models.engine)
