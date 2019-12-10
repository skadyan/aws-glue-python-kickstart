from osiris.aws import s3
from osiris.base.environments import YamlPropertySource


def example():
    bucket = "osiris-app-home"
    file = "apps/osiris/conf/defaults.yaml"

    with s3.open_s3(bucket, file) as fp:
        source = YamlPropertySource.load_from(fp, file)
    print(source)


if __name__ == '__main__':
    example()
