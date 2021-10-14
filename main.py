from data_api_ree import DataAPIRee

def main () -> None:
    print("profesor watio main starting...")
    api_ree = DataAPIRee()
    print (api_ree.get_today_kwh_price())
    #now insert in mongodb


if __name__ == "__main__":
    main()