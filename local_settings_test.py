# -*- coding: utf-8 -*-

API_BASE = "http://127.0.0.1:8282/"

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
PREAMBLE_INTRO = {
    "2016_02749": {
        "tree": {
            "title": "Preamble introduction",
            "text": "",
            "node_type": "preamble_intro",
            "label": ["2016_02749", "intro"],
            "children": [
                {"title": "Summary:",
                 "text": """The U.S. Environmental Protection Agency (EPA) is
                 proposing to add a subsurface intrusion (SsI) component to
                 the Hazard Ranking System (HRS) which is the principal
                 mechanism that EPA uses to evaluate sites for placement on
                 the National Priorities List (NPL). The subsurface intrusion
                 component (this addition) would expand the number of
                 available options for EPA and state and tribal organizations
                 performing work on behalf of EPA to evaluate potential
                 threats to public health from releases of hazardous
                 substances, pollutants, or contaminants. This addition will
                 allow an HRS evaluation to directly consider human exposure
                 to hazardous substances, pollutants, or contaminants that
                 enter regularly occupied structures through subsurface
                 intrusion in assessing a site's relative risk, and thus,
                 enable subsurface intrusion contamination to be evaluated for
                 placement of sites on the NPL. The agency is not considering
                 changes to the remainder of the HRS except for minor updates
                 reflecting changes in terminology.""",
                 "node_type": "preamble",
                 "label": ["2016_02749", "intro", "p3"],
                 "children": []},
                {"title": "Dates:",
                 "text": ("Comments must be received on or before April "
                          "29, 2016."),
                 "node_type": "preamble",
                 "label": ["2016_02749", "intro", "p4"],
                 "children": []},
                {"title": "Addresses:",
                 "text": """Submit your comments, identified by Docket ID No.
                 EPA-HQ-SFUND-2010-1086, to the Federal eRulemaking Portal:
                 http://www.regulations.gov. Follow the online instructions
                 for submitting comments. Once submitted, comments cannot be
                 edited or withdrawn. The EPA may publish any comment received
                 to its public docket. Do not submit electronically any
                 information you consider to be Confidential Business
                 Information (CBI) or other information whose disclosure is
                 restricted by statute. Multimedia submissions (audio, video,
                 etc.) must be accompanied by a written comment. The written
                 comment is considered the official comment and should include
                 discussion of all points you wish to make. The EPA will
                 generally not consider comments or comment contents located
                 outside of the primary submission (i.e. on the Web, cloud, or
                 other file sharing system). For additional submission
                 methods, the full EPA public comment policy, information
                 about CBI or multimedia submissions, and general guidance on
                 making effective comments, please visit
                 http://www.epa.gov/dockets/commenting-epa-dockets.""",
                 "node_type": "preamble",
                 "label": ["2016_02749", "intro", "p5"],
                 "children": []},
                {"title": "For further information contact:",
                 "text": """Terry Jeng, phone: (703) 603-8852, email:
                 jeng.terry@epa.gov, Site Assessment and Remedy Decisions
                 Branch, Assessment and Remediation Division, Office of
                 Superfund Remediation and Technology Innovation (Mail Code
                 5204P), U.S. Environmental Protection Agency, 1200
                 Pennsylvania Avenue NW., Washington, DC 20460; or the
                 Superfund Hotline, phone (800) 424-9346 or (703) 412-9810 in
                 the Washington, DC metropolitan area.""",
                 "node_type": "preamble",
                 "label": ["2016_02749", "intro", "p6"],
                 "children": []}
                ]},
        "meta": {
            "primary_agency": "Environmental Protection Agency",
            "agencies": ["Environmental Protection Agency"],
            "action": "Proposed rule",
            "title": ("Addition of a Subsurface Intrusion Component to the "
                      "Hazard Ranking System"),
            "comments_close": "2016-04-29",
            "publication": "2016-02-29",
            "cfr_parts": [{"title": "40", "parts": ["300"]}],
            "dockets": ["EPA-HQ-SFUND-2010-1086",
                        "FRL-9925-69-OLEM"],
            "rins": ["2050-AG67"],
        }
    }
}
