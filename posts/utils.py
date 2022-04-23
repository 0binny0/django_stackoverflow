
import re

def retrieve_query_title(string):
    title_pattern = re.compile(r"(?<=title:)\s*(?P<title>([^\[\]])*)")
    query_title = title_pattern.search(string)
    '''query_title[0].strip() checks whether string is truthy'''
    if query_title and query_title[0].strip():
        non_reserved_characters = re.compile(r"([^*!#$&'()*+,/:;=?%@\[\]<>\s]+)")
        query_title = " ".join(map(
            lambda word: word.lower().strip(),
            non_reserved_characters.findall(query_title.group("title"))
        ))
        user_id_pattern_in_title = re.search(r"user", query_title)
        if user_id_pattern_in_title:
            pos = user_id_pattern_in_title.start()
            query_title = query_title[0:pos].strip()
        return query_title
    return None

def retrieve_query_tags(string):
    contained_tags = list(map(
        lambda match: re.sub(r"[*!#$&'\"()%*+,/:;=?@\[\]<>\s]", "", match[0])
        , re.finditer(r"(?<=\[)[^\[\]]+(?=\])", string)
    ))
    if all(not tag for tag in contained_tags):
        return None
    tag_content = list(map(
        lambda match: "-".join(
            re.findall(r"([a-zA-Z0-9]+)", match.lower())
        ), filter(lambda tag: tag, contained_tags)
    ))[:2]
    return tag_content

def retrieve_query_user_id(string):
    # import pdb; pdb.set_trace()
    user_id_search = re.compile(r"(?<=user:)(\d+)")
    searching_by_user = user_id_search.search(string)
    if searching_by_user:
        # user_id = re.search(r"(\d+)", searching_by_user[0])
        return int(searching_by_user[0])
        # user_id = "".join(re.search(r"(\d+)", searching_by_user[0]))
        # if user_id:
        #     return int(user_id)
    return None

def resolve_search_query(string):
    search_query_title = retrieve_query_title(string)
    search_tags = retrieve_query_tags(string)
    search_user = retrieve_query_user_id(string)
    return {
        'title': search_query_title,
        'tags': search_tags,
        'user': search_user
    }
