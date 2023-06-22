from specklepy.api.client import SpeckleClient
from gql import gql


def make_comment(
    client: SpeckleClient,
    project_id: str,
    model_id: str,
    version_id: str,
    comment_text: str,
    selected_object_id: str,
) -> None:
    client.httpclient.execute(
        gql(
            """
            mutation createComment($input: CreateCommentInput!) {
                commentMutations {
                    create(input: $input) {
                    id
                    }
                }
            }
        """
        ),
        {
            "input": {
                "content": {
                    "blobIds": [],
                    "doc": {
                        "content": [
                            {
                                "content": [{"text": comment_text, "type": "text"}],
                                "type": "paragraph",
                            }
                        ],
                        "type": "doc",
                    },
                },
                "projectId": project_id,
                "resourceIdString": model_id,
                "screenshot": None,
                "viewerState": {
                    "projectId": project_id,
                    "resources": {
                        "request": {
                            "resourceIdString": f"{model_id}@{version_id}",
                            "threadFilters": {},
                        }
                    },
                    "sessionId": "fooobarbaz",
                    "ui": {
                        "camera": {
                            "isOrthoProjection": False,
                            "position": [
                                -13.959975903859306,
                                109.21340462426888,
                                19.00868018548827,
                            ],
                            "target": [
                                -28.304303646087646,
                                99.69336318969727,
                                2.3997000455856323,
                            ],
                            "zoom": 1,
                        },
                        "explodeFactor": 0,
                        "filters": {
                            "hiddenObjectIds": [],
                            "isolatedObjectIds": [selected_object_id],
                            "propertyFilter": {"isApplied": False, "key": None},
                            "selectedObjectIds": [selected_object_id],
                        },
                        "lightConfig": {
                            "azimuth": 0.75,
                            "castShadow": True,
                            "color": 16777215,
                            "elevation": 1.33,
                            "enabled": True,
                            "indirectLightIntensity": 1.2,
                            "intensity": 5,
                            "radius": 0,
                            "shadowcatcher": True,
                        },
                        "sectionBox": None,
                        "selection": [
                            -31.355755138199026,
                            101.06821903317298,
                            4.250507316347136,
                        ],
                        "spotlightUserSessionId": None,
                        "threads": {
                            "openThread": {
                                "isTyping": False,
                                "newThreadEditor": True,
                                "threadId": None,
                            }
                        },
                    },
                    "viewer": {"metadata": {"filteringState": {}}},
                },
            }
        },
    )
