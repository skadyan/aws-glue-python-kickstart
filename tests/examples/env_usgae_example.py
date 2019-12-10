from osiris.base.environments import env


def example():
    value = env.get_property("sys.aws.region_name")
    print(value)


if __name__ == '__main__':
    example()
