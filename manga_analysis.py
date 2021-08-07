import logging
import platform
from pathlib import Path

import matplotlib.pyplot as plt

from src.crop_api import ImageSaliencyModel

logging.basicConfig(level=logging.ERROR)


def main(manga_id,
         data_dirname="./data/",
         num_limit=10000,
         save_fig=False,
         verbose=False):
    # prepare directories
    home_dir = Path("./").expanduser()
    bin_dir = home_dir / "./bin"
    platform_dirname_map = {"Darwin": "mac", "Linux": "linux"}
    platform_dirname = platform_dirname_map[platform.system()]
    bin_path = bin_dir / platform_dirname / "candidate_crops"
    model_path = bin_dir / "fastgaze.vxm"
    result_dir = home_dir / "results" / manga_id
    result_dir.mkdir(exist_ok=True)
    data_dir = home_dir / data_dirname / manga_id
    assert data_dir.exists()

    model = ImageSaliencyModel(crop_binary_path=bin_path,
                               crop_model_path=model_path)

    img_paths = list(data_dir.glob("*.png")) + list(data_dir.glob("*.jpg"))
    img_paths = sorted(img_paths)[:num_limit]
    for img_path in img_paths:
        print(img_path)
        model.plot_img_crops(img_path, saliency_line_y=True)
        if save_fig:
            plt.savefig(result_dir / img_path.name, bbox_inches="tight")
        plt.clf()
        plt.close()

    all_results = model.get_all_results()
    for results in all_results:
        img_w = results['img_w']
        img_h = results['img_h']
        results['normalized_my'] = [y / img_h for y in results['my']]
        salient_y = results['salient_point'][0][1]
        results['normalized_salient_y'] = salient_y / img_h
        if verbose:
            print(img_w, img_h)
            print(results['salient_point'])
            print(results['normalized_salient_y'])
            print(results['crops'])
            print(results['normalized_my'])
            print(results['mz'])
            print()
    norm_y = [results['normalized_salient_y'] for results in all_results]

    fig = plt.figure(constrained_layout=False, figsize=(6, 4))
    plt.hist(norm_y, bins=20, range=(0., 1.))
    plt.title(f'{manga_id}x{len(all_results)}')
    plt.xlabel('Normalized salient y')
    plt.ylabel('Frequency')
    fig.tight_layout()
    plt.savefig(result_dir / 'norm_y_hist.png', bbox_inches="tight")


if __name__ == '__main__':
    num_limit_map = {'shiny4': 250, 'pri4': 250, 'girl4': 250, 'negi4': 1000}
    manga_ids = ['shiny4', 'pri4', 'girl4', 'negi4']
    for manga_id in manga_ids:
        num_limit = num_limit_map[manga_id]
        main(manga_id, data_dirname="./data/", num_limit=num_limit)
