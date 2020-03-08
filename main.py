import argparse
import gender

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image")

    args = parser.parse_args()
    genders = gender.resolve(args.image)

    for g in genders:
        print(g)

if __name__ == "__main__":
    main()
