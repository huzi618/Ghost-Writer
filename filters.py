ALLOWED_COMPARATORS = [
                "$eq",
                "$in",]

EXAMPLES = [
                (
                    "Write me a song in the style of Billie Eilish.",
                    {
                        "query": "Billie Eilish",
                        "filter": 'eq(\"writer\", \"Billie Eilish\")',
                    },
                ),
                (
                    "Write a song similar to Tamino's songs.",
                    {
                        "query": "Tamino",
                        "filter": 'eq(\"writer\", \"Tamino\")',
                    },
                ),

                (
                    "Use Pink Floyd's writing style and write me a song.",
                    {
                        "query": "Pink Floyd",
                        "filter": 'eq(\"writer\", \"Pink Floyd\")',
                    },
                ),
            ]