from typing import Optional


def get_flags_from_command(cmd: str) -> Optional[dict]:
    flags_values = cmd.split('-')[1:]
    res = {}

    for flag_value in flags_values:
        flag_value = flag_value.split(' ', 1)

        if len(flag_value) == 2:
            flag, value = flag_value
        else:
            return None

        res[flag] = value

    return res


if __name__ == '__main__':
    print(get_flags_from_command('/login -key бляха муха -name BERKYT'))
    print(get_flags_from_command('/login -name BERKYT -key бляха муха -sd'))

