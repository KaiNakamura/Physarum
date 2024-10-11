import os
from skele import PictureToNetwork


def main():
    for filename in os.listdir("figures"):
        ptn = PictureToNetwork(f"figures/{filename}")
        ptn.run()
        ptn.display_results()
        # ptn.dump_graph("output")


if __name__ == "__main__":
    main()
