# snapshottest: v1 - https://goo.gl/zC4yUc

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots[
    "test_graph 1"
] = """digraph G {
concentrate=False;
mode=ipsep;
overlap=ipsep;
prog=dot;
rankdir=LR;
sep="0.01";
user_prefs [fontname="Bitstream-Vera Sans", fontsize="7.0", label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0"><TR><TD ALIGN="CENTER">user_prefs</TD></TR><TR><TD BORDER="1" CELLPADDING="0"></TD></TR><TR><TD ALIGN="LEFT" PORT="pref_id">- pref_id</TD></TR><TR><TD ALIGN="LEFT" PORT="user_id">- user_id</TD></TR><TR><TD ALIGN="LEFT" PORT="pref_name">- pref_name</TD></TR><TR><TD ALIGN="LEFT" PORT="pref_value">- pref_value</TD></TR></TABLE>>, shape=plaintext];
user [fontname="Bitstream-Vera Sans", fontsize="7.0", label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0"><TR><TD ALIGN="CENTER">user</TD></TR><TR><TD BORDER="1" CELLPADDING="0"></TD></TR><TR><TD ALIGN="LEFT" PORT="user_id">- user_id</TD></TR><TR><TD ALIGN="LEFT" PORT="user_name">- user_name</TD></TR><TR><TD ALIGN="LEFT" PORT="email_address">- email_address</TD></TR><TR><TD ALIGN="LEFT" PORT="nickname">- nickname</TD></TR></TABLE>>, shape=plaintext];
}
"""
