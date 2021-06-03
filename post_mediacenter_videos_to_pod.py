#!/usr/bin/env python3
"""Upload video to pod"""

import argparse
import os

from dotenv import load_dotenv
import MySQLdb
import requests

load_dotenv()

AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
MEDIACENTER_DATABASE_HOST = os.environ.get("MEDIACENTER_DATABASE_HOST", "localhost")
MEDIACENTER_DATABASE_PORT = int(os.environ.get("MEDIACENTER_DATABASE_PORT", "3306"))
MEDIACENTER_DATABASE_NAME = os.environ.get("MEDIACENTER_DATABASE_NAME", "mediacenter")
MEDIACENTER_DATABASE_USER = os.environ.get("MEDIACENTER_DATABASE_USER", "mediacenter")
MEDIACENTER_DATABASE_PASSWORD = os.environ.get("MEDIACENTER_DATABASE_PASSWORD")
MEDIACENTER_VIDEOS_FOLDER = os.environ.get("MEDIACENTER_VIDEOS_FOLDER")
PODINSTANCE = os.environ.get("PODINSTANCE")


def get_pod_cas_users(pod_users, pod_owners):
    """Return all users which authenticate using CAS."""
    pod_cas_owners_user_url = [
        pod_owner["user"] for pod_owner in pod_owners if pod_owner["auth_type"] == "CAS"
    ]

    pod_cas_users = [
        pod_user for pod_user in pod_users if pod_user["url"] in pod_cas_owners_user_url
    ]

    return pod_cas_users


def collect_arguments():
    """Collect command line arguments"""
    parser = argparse.ArgumentParser(
        description="""
        Retrive videos from Inwicast Mediacenter and upload them to a Pod instance
    """
    )
    required_arguments = parser.add_argument_group("Required arguments")
    required_arguments.add_argument(
        "--type-id",
        required=True,
        help="Video's type id",
        metavar="TYPEID",
    )
    required_arguments.add_argument(
        "--admin-id",
        required=True,
        help="Id of a pod user having admin rights",
        metavar="ADMINID",
    )
    required_arguments.add_argument(
        "--site-id",
        required=True,
        help="Pod site id",
        metavar="SITEID",
    )
    return parser.parse_args()


def get_mediacenter_videos_data():  # pylint: disable=missing-function-docstring
    """
    Get informations to be used when uploading videos to pod and also the path the video to upload
    """
    db_connection = MySQLdb.connect(
        host=MEDIACENTER_DATABASE_HOST,
        port=MEDIACENTER_DATABASE_PORT,
        user=MEDIACENTER_DATABASE_USER,
        passwd=MEDIACENTER_DATABASE_PASSWORD,
        db=MEDIACENTER_DATABASE_NAME,
    )
    db_cursor = db_connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    db_cursor.execute(
        """
        SELECT
            user_name,
            title,
            description,
            !is_public as is_restricted,
            is_downloadable as allow_downloading,
            media_ref
        FROM mdcr_inwicast_medias
        WHERE media_type = 'podvideo';
    """
    )
    videos_data = db_cursor.fetchall()
    db_cursor.close()
    return videos_data


def get_user_id_or_admin_id(mapping_pod_cas_users_username_id, username, admin_id):
    """
    Check if a given pod CAS user based on its username exists and return its id.
    If it does not exists, it is admin user's id which is returned
    """

    if username in mapping_pod_cas_users_username_id.keys():
        return mapping_pod_cas_users_username_id[username]
    return admin_id


def upload_video_to_pod(video_path, owner_id, type_id, site_id, title, **optional_data):
    """Upload a video to Pod using data provided"""
    with open(video_path, "rb") as video_file:
        video_content = video_file.read()
    data = {
        "owner": "{}/rest/users/{}/".format(PODINSTANCE, owner_id),
        "type": "{}/rest/types/{}/".format(PODINSTANCE, type_id),
        "sites": "{}/rest/sites/{}/".format(PODINSTANCE, site_id),
        "title": "{}".format(title),
        **optional_data,
    }
    post_video_response = requests.post(
        "{}/rest/videos/".format(PODINSTANCE),
        headers={
            "Authorization": "Token {}".format(AUTH_TOKEN),
        },
        data=data,
        files={"video": video_content},
    )
    return post_video_response.json()["slug"]


def launch_video_encoding(video_slug):
    """Launch the encoding of the video corresponding to the slug passed in argument"""
    requests.get(
        "{}/rest/launch_encode_view/".format(PODINSTANCE),
        params={"slug": video_slug},
        headers={"Authorization": "Token {}".format(AUTH_TOKEN)},
    )


def main():
    """Entry point of the script"""
    args = collect_arguments()
    mediacenter_videos_data = get_mediacenter_videos_data()

    pod_users = requests.get(
        "{}/rest/users/".format(PODINSTANCE),
        headers={"Authorization": "Token {}".format(AUTH_TOKEN)},
    ).json()["results"]
    pod_owners = requests.get(
        "{}/rest/owners/".format(PODINSTANCE),
        headers={"Authorization": "Token {}".format(AUTH_TOKEN)},
    ).json()["results"]
    pod_cas_users = get_pod_cas_users(pod_users, pod_owners)
    mapping_pod_cas_users_username_id = {
        user["username"]: user["id"] for user in pod_cas_users
    }
    for video_data in mediacenter_videos_data:
        optional_data = {
            key: value
            for (key, value) in video_data.items()
            if value and key not in ["user_name", "title", "media_ref"]
        }
        owner_id = get_user_id_or_admin_id(
            mapping_pod_cas_users_username_id, video_data["user_name"], args.admin_id
        )
        video_slug = upload_video_to_pod(
            "{0}/{1}/multimedia/{1}.mp4".format(
                MEDIACENTER_VIDEOS_FOLDER, video_data["media_ref"]
            ),
            owner_id,
            args.type_id,
            args.site_id,
            video_data["title"],
            **optional_data,
        )

        launch_video_encoding(video_slug)


if __name__ == "__main__":
    main()
