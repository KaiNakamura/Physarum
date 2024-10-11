import os
from skele import PictureToNetwork


def main():
    for filename in os.listdir("figures"):
        ptn = PictureToNetwork(
            f"figures/{filename}",
            keep=[  # The foods for the files
                (524, 129),
                (608, 229),
                (583, 272),
                (598, 322),
                (595, 393),
                (529, 452),
                (567, 560),
                (617, 587),
                (395, 373),
                (218, 388),
                (408, 320),
            ],
        )
        ptn.run()
        ptn.display_results()
        ptn.dump_graph("output")


if __name__ == "__main__":
    main()
