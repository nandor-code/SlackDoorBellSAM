# SlackDoorBellSAM
---
## Requirements

1) Working Slack Server
2) Working Slack Bot / App with Token

## Installation

> $ aws rekognition create-collection --collection-id my_collection --region eu-west-1 

### Edit template.yaml and change ntsj_collection to my_collection in the 2 policy sections.

### Finally goto AWS Console -> AWS Systems Manager -> Parameter Store -> New SecureString
#### Name: SlackDoorBellConfig
#### Value: "token": "xoxb-myslackbottoken","collection": "my_collection","channel": "my_slack_channel"}
