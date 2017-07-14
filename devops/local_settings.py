# -*- coding: utf-8 -*-
from datetime import date, timedelta

REGS_GOV_API_MOCK = True

CFR_CHANGES = {
    "2016_02749": {
        "versions": {
            "478": {"left": "2010-13392", "right": "2012-13762"}
        },
        "amendments": [
            {"instruction": """
                1. The authority citation for 27 CFR part 478 is revised to
                read as follows:""",
             "cfr_part": "478",
             "authority":
                '5 U.S.C. 552(a); 18 U.S.C. 847, 921-931; 44 U.S.C. 3504(h).'},
            {"instruction": u"""
                2. Section 478.11 is amended by adding a definition for the
                term “Nonimmigrant visa” in alphabetical order to read as
                follows:""",
             "cfr_part": "478",
             "changes": [["478-11-p242755046", []]]},
            {"instruction": """
                3. Section 478.32 is amended by revising the introductory text
                of paragraphs (a)(5)(ii) and (d)(5)(ii), and by revising
                paragraph (f), to read as follows:""",
             "cfr_part": "478",
             "changes": [["478-32-a-5-ii", []],
                         ["478-32-d-5-ii", []],
                         ["478-32-f", []]]},
            {"instruction": """
                4. Section 478.44 is amended by revising paragraph
                (a)(1)(iii), and by revising the second sentence in paragraph
                (b), to read as follows:""",
             "cfr_part": "478",
             "changes": [["478-44-a-1-iii", []],
                         ["478-44-b", []]]},
            {"instruction": """
                5. Section 478.45 is amended by revising the second sentence
                to read as follows:""",
             "cfr_part": "478",
             "changes": [["478-45", []]]},
            {"instruction": """
                6. Section 478.99 is amended by revising the introductory text
                of paragraph (c)(5) to read as follows:""",
             "cfr_part": "478",
             "changes": [["478-99-c-5", []]]},
            {"instruction": """
                7. Section 478.120 is revised to read as follows:""",
             "cfr_part": "478",
             "changes": [["478-120", []]]},
            {"instruction": """
                8. Section 478.124 is amended by revising paragraph
                (c)(3)(iii) to read as follows:""",
             "cfr_part": "478",
             "changes": [["478-124-c-3-iii", []]]}
        ]
    }
}
future = date.today() + timedelta(days=10)
PREAMBLE_INTRO = {
    "2016_02749": {
        "meta": {
            "primary_agency": "Environmental Protection Agency",
            "agencies": ["Environmental Protection Agency"],
            "action": "Proposed rule",
            "title": ("Addition of a Subsurface Intrusion Component to the "
                      "Hazard Ranking System"),
            "comments_close": future.isoformat(),
            "publication_date": "2016-02-29",
            "cfr_title": 40,
            "cfr_parts": ["300"],
            "dockets": ["EPA-HQ-SFUND-2010-1086",
                        "FRL-9925-69-OLEM"],
            "regulation_id_numbers": ["2050-AG67"],
        }
    }
}
