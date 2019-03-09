# dndtools
Slack app that provides slash commands for D&D 5E gamers. It contains three main user functions:
* /condition - gives the effects of the named condition, e.g., `/condition exhaustion`
* /roll - roll some dice, e.g., `/roll 3d6`
* /spellbook - get the text of the named spell, e.g., `/spellbook Fireball`
![alt text](docs/dndtools-screenshot.png "dndtools in action")
## Quickstart
This app supports a Slack app to provide custom [slash commands](https://api.slack.com/slash-commands). It uses [Zappa](https://github.com/Miserlou/Zappa) to deploy a [Flask](http://flask.pocoo.org/) application to [AWS Lambda](https://aws.amazon.com/lambda/) and uses [AWS DynamoDB](https://aws.amazon.com/dynamodb/) as its data source.

To start, create a [Slack app](https://api.slack.com/slack-apps). Make sure your [AWS Credentials](https://aws.amazon.com/blogs/security/a-new-and-standardized-way-to-manage-credentials-in-the-aws-sdks/) file is up to date or create it if you don't have one.

### Download the repo and install requirements
I recommend you use virtualenv to create a virtual environment for running this code and downloading all its dependencies. More info on virtualenv [here](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/) if you're not familiar.

```sh
git clone https://github.com/gwrome/dndtools.git
cd dndtools
pip install -r requirements.txt
```

### Initialize the database
Once you're ready to initialize the database, it's as easy as 

```sh
FLASK_APP=dndtools.py flask init-db
```

#### Optional: Custom Spell Lists
By default, the app uses the [srd-spells.json](dndtools/srd-spells.json) file to populate the database with spells. If you have custom spells in the same format, you can pass the `--infile <filename>` argument to `init-db` command, like so: `FLASK_APP=dndtools.py flask init-db --infile customfile.json`. The app also knows how to read the JSON file format used in the resources from [5e.tools](http://5e.tools), which are also [available on Github](https://github.com/TheGiddyLimit/TheGiddyLimit.github.io). If using a JSON file in that format, use the `--tools` flag: `FLASK_APP=dndtools.py flask init-db --infile <filename> --tools`.

#### Optional: Local DynamoDB
If you're planning to run the application locally, you need to install a [local DynamoDB server](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html). Set a few environment variables to make things work locally:
```
DYNAMO_ENABLE_LOCAL=True
DYNAMO_LOCAL_HOST=localhost-or-other-host
DYNAMO_LOCAL_PORT=8000-or-other-port
```

### Deploy
Deploy the app to AWS Lambda using Zappa:
```sh
pip install zappa
zappa init
```

`zappa init` will create a zappa_settings.json file, which you can edit as necessary. Make sure your stage definition sets

`"app_function": "zappa_init.app"`

Once Zappa's settings are configured:
```sh
zappa deploy <stagename>
```

If you're running the app locally, you're already deployed. You can use a service like [ngrok](https://ngrok.com/) to tunnel through a NAT firewall to your local machine when setting up the Slack app endpoints.

### Set up Slack
In your Slack app, you need to set up three slash commands—`/condition`, `/roll`, and `/spellbook` that point to the corresponding endpoints on AWS Lambda or on your local machine. There's a great guide (with pictures!) to doing that [here](https://renzo.lucioni.xyz/serverless-slash-commands-with-python/).

#### Slack environment variables
No matter where you run the server, it needs to know your Slack verification token and your Slack Team ID. If running locally, you can set them as environment variables in the usual ways. If you're running the app in Lambda, you can set the environment variables in your lambda's configuration panel.
```
SLACK_VERIFICATION_TOKEN=your-verification-token
SLACK_TEAM_ID=your-team-id
```

## Acknowledgements
Thanks to Renzo Luciono's great [tutorial on serverless slash commands](https://renzo.lucioni.xyz/serverless-slash-commands-with-python/). That's where this app started, and I couldn't have juggled all the pieces from the start without his guidance.

And thanks to GitHub user vorpalhex for packaging up the SRD's spells in a [handy JSON file](https://github.com/vorpalhex/srd_spells) that I've included with this repo.

## Open Gaming License Content
The contents of [srd-spells.json](dndtools/srd-spells.json), [raw_spells.json](tests/raw_spells.json), and the condition information in [condition.py](dndtools/condition.py) are used under the Open Gaming License. I have also included a copy of the relevant [OGL in the repo](ogl.html). No other content in this repository is subject to the OGL.
