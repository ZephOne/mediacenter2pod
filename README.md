# Post video from Inwicast Mediacenter to Pod

## Synopsis

This script aims to upload videos stored in an [Inwicast MediaCenter](http://www.inwicast.com/mediacenter3/) instance to a [Pod](https://github.com/EsupPortail/Esup-Pod) instance.

This script directly uses Inwicast MediaCenter database to get informations about videos (title, description, video reference...), then you need your Inwicast MediaCenter database to be accessible by your script.
In addition, your videos need to be on the script's file system.

Videos are upload using metadata from mediacenter: description, owner, title, video is public, video is downloadable.

Concerning the owner.
If the owner uses the same CAS system to authenticate to the MediaCenter instance and to the Pod instance and the owner is in the Pod database then this user will be specified as owner of the uploaded video.
Otherwise, an admin user will be specify as owner.

## Installation

* Clone the repository:

```bash
git clone <url of the remote repository>
```

* Go in your local repository.
* Create a virtual environment:

```bash
python3 -m virtualenv --python python3 venv
```

* Activate your virtual environment:

```bash
. venv/bin/activate
```

* Install python dependencies:

```bash
pip install -r requirements.txt
```


## Usage

```bash
python post_video_to_pod.py --help
usage: post_video_to_pod.py [-h] --type-id TYPEID --admin-id ADMINID --site-id SITEID

Retrive videos from Inwicast Mediacenter and upload them to a Pod instance

optional arguments:
  -h, --help          show this help message and exit

Required arguments:
  --type-id TYPEID    Video's type id
  --admin-id ADMINID  Id of a pod user having admin rights
  --site-id SITEID    Pod site id
```

## Configuration

Configuration is made using the [python-dotenv](https://pypi.org/project/python-dotenv/) library.
You can use the file `.env.dist` to easily start your configuration:

```bash
cp .env.dist .env
```

Then configure your script using the following variables

| Variable                        | Description                                                    | Default       |
|---------------------------------|----------------------------------------------------------------|---------------|
| `AUTH_TOKEN`                    | Your token to use the Pod instance API (admin rights required) | ""            |
| `MEDIACENTER_DATABASE_HOST`     | Host of your database                                          | "localhost"   |
| `MEDIACENTER_DATABASE_PORT`     | Port your database is listening to                             | 3306          |
| `MEDIACENTER_DATABASE_NAME`     | Name of your database                                          | "mediacenter" |
| `MEDIACENTER_DATABASE_USER`     | User of your database                                          | "mediacenter" |
| `MEDIACENTER_DATABASE_PASSWORD` | Password to connect to your database                           | ""            |
| `MEDIACENTER_VIDEOS_FOLDER`     | Path to your folder containing your MediaCenter videos         | ""            |
| `PODINSTANCE`                   | Url of your pod instance (e.g https://pod.univ.fr)             | ""            |

