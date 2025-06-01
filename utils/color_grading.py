def get_color_filter(mood):
    """
    Return FFmpeg color grading filter string based on mood category.
    """

    filters = {
        "none": "",
        "warm": "colorbalance=rs=.3:gs=.1:bs=-.2",
        "cool": "colorbalance=rs=-.2:gs=.1:bs=.3",
        "cinematic": "curves=r='0/0 0.5/0.7 1/1':g='0/0 0.5/0.6 1/1':b='0/0 0.5/0.8 1/1'",
        "vintage": "hue=s=0:s=0.5",
        "cyberpunk": "eq=contrast=1.5:brightness=0.05:saturation=2",
    }

    return filters.get(mood.lower(), "")
