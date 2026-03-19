def get_images():
    images = {
        "camp_1.jpg": "A cabin built in the 1920's at summer camp in South Carolina",
        "camp_2.jpg": "The pine trees at summer camp in South Carolina",
        "camp_3.jpg": "The woods at summer camp in South Carolina",

        "changshu_garden_1.jpg": "The ancient Zhaoyuan Garden complex in Changshu, China",
        "changshu_garden_2.jpg": "The ancient Zhaoyuan Garden complex in Changshu, China",
        "changshu_garden_3.jpg": "The ancient Zhaoyuan Garden complex in Changshu, China",
        "changshu_garden_4.jpg": "The ancient Zhaoyuan Garden complex in Changshu, China",
        "changshu_garden_5.jpg": "The ancient Zhaoyuan Garden complex in Changshu, China",
        "changshu_garden_6.jpg": "The ancient Zhaoyuan Garden complex in Changshu, China",
        "changshu_garden_7.jpg": "The ancient Zhaoyuan Garden complex in Changshu, China",
        "changshu_garden_8.jpg": "The ancient Zhaoyuan Garden complex in Changshu, China",
        "changshu_garden_9.jpg": "The ancient Zhaoyuan Garden complex in Changshu, China",
        "changshu_garden_10.jpg": "The ancient Zhaoyuan Garden complex in Changshu, China",
        "changshu_garden_11.jpg": "The ancient Zhaoyuan Garden complex in Changshu, China",

        "changzhou_institute_of_technology_1.jpg": "A view from a building at Changzhou Institute of Technology, Changzhou, China",
        "changzhou_institute_of_technology_2.jpg": "A view from a building at Changzhou Institute of Technology, Changzhou, China",
        "changzhou_institute_of_technology_3.jpg": "A view from a building at Changzhou Institute of Technology, Changzhou, China",

        "changzhou_old_city_1.jpg": "A bridge in the ancient section of Changzhou, China",

        "changzhou_pagota_1.jpg": "A view from the Tianning pagoda in Changzhou, China",
        "changzhou_pagota_2.jpg": "A building in the Tianning Temple in Changzhou, China",
        "changzhou_pagota_3.jpg": "A view from the Tianning pagoda in Changzhou, China",

        "dc_1.jpg": "Somewhere in Washington DC",

        "door_county_1.jpg": "A dam in Door County, Wisconsin",
        "door_county_2.jpg": "A view of Lake Michigan in Door County, Wisconsin",

        "florida_1.jpg": "A beach in Vero Beach, Florida",
        "florida_2.jpg": "A beach in Vero Beach, Florida",
        "florida_3.jpg": "A beach in Vero Beach, Florida",
        "florida_4.jpg": "A beach in Vero Beach, Florida",
        "florida_5.jpg": "A beach in Vero Beach, Florida",

        "kennedy_1.jpg": "The space shuttle Atlantis in Kennedy Space Center",
        "kennedy_2.jpg": "A NASA launch pad at Kennedy Space Center",
        "kennedy_3.jpg": "The end of a Saturn V rocket at Kennedy Space Center",
        "kennedy_4.jpg": "The end of a Saturn V rocket at Kennedy Space Center",
        "kennedy_5.jpg": "The end of a Saturn V rocket at Kennedy Space Center",
        "kennedy_6.jpg": "The rocket garden at Kennedy Space Center",

        "shanghai_1.jpg": "The iconic cityscape in Shanghai, China",

        "uwec_1.jpg": "A view of the Chippewa river and some of the campus at UW-Eau Claire, Wisconsin (My undergrad)",
        "uwec_2.jpg": "A view of some of the campus at UW-Eau Claire, Wisconsin (My undergrad)",
        "uwec_3.jpg": "A view of the Chippewa river and some of the campus at UW-Eau Claire, Wisconsin (My undergrad)",
        "uwec_4.jpg": "A view of the overflowing Chippewa river at UW-Eau Claire, Wisconsin (My undergrad)",
        "uwec_5.jpg": "A view of the Chippewa river at UW-Eau Claire, Wisconsin (My undergrad)",
        "uwec_6.jpg": "A snowy view of Davies student center at UW-Eau Claire, Wisconsin (My undergrad)",
        "uwec_7.jpg": "A view of the Chippewa river and some of the campus at UW-Eau Claire, Wisconsin (My undergrad)",
        "uwec_8.jpg": "A view of Schofield hall (my favorite campus building) at UW-Eau Claire, Wisconsin (My undergrad)",
        "uwec_9.jpg": "A view of the Chippewa river at UW-Eau Claire, Wisconsin (My undergrad)",


        "wyalusing_1.jpg": "A view of the Mississippi river at Wyalusing state park, Wisconsin"
    }

    return images


def get_caption(filename):
    images = get_images()

    for i in images:
        if i==filename:
            return images[i]