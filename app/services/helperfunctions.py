import requests
import constants








def getPercentChange(current, previous) ->str:
    return str((current - previous)/previous * 100) + "%"


if __name__ == "__main__":
    # print(getFinancials("msft"))
    # print(getNews("msft"))
    # print(getInfo("msft"))
    print(getInfo("aple"))