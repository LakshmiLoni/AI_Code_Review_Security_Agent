def calculate_total(price, quantity):
    total = price * quantity
    return total


def main():
    result = calculate_total(100, 3)
    print("Total:", result)


if __name__ == "__main__":
    main()