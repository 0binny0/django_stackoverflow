
import re

def retrieve_exact_phrase(string):
    import pdb; pdb.set_trace()
    string_pattern = re.compile(r"([\"|\'])+(?P<phrase>.+)\1+")
    phrase = string_pattern.search(string)
    if phrase:
        return phrase.groupdict()['phrase']
    return None

def retrieve_query_title(string):
    title_pattern = re.compile(r'(?<=title:)\s*(?P<title>([^\[\]<>]+))')
    # title_pattern = re.compile(r"(?<=title:)\s*(?<=[\"|'])(?P<title>\w+)(?=[\"|'])")
    query_title = title_pattern.search(string)
    '''query_title[0].strip() checks whether string is truthy'''
    if query_title:
        title = query_title[0].strip()
        non_reserved_characters = re.compile(r"([^\[\]<>\s]+)")
        title = " ".join(map(
            lambda word: word.strip(),
            non_reserved_characters.findall(query_title.group("title"))
        ))
        user_id_pattern_in_title = re.search(r"(\buser:{1,}\d+\b)", title)
        if user_id_pattern_in_title:
            user_id_start_pos, user_id_end_pos = user_id_pattern_in_title.span()
            if user_id_start_pos == 0:
                title = title[user_id_end_pos + 1:].strip()
            elif user_id_end_pos == len(title) - 1:
                title = title[0:user_id_start_pos].strip()
            else:
                title = f"{title[:user_id_start_pos]}{title[user_id_end_pos + 1:]}".strip()
        title_string = title.strip('\'"')
        if title_string:
            return title_string
    return None

def retrieve_query_tags(string):

    contained_tags = list(map(
        lambda match: re.sub(r"[*!$&'\"()%*,/:;=@\[\]<>\s]", "", match[0])
        , re.finditer(r"(?<=\[)[^\[\]]+(?=\])", string)
    ))
    if all(not tag for tag in contained_tags):
        return None
    tag_content = list(map(
        lambda string_match: string_match[1:]
        if string_match[0] == "#" and re.search(r"(?<=#)\w", string_match) else string_match,
        map(
            lambda match: "-".join(
                re.findall(r"([a-zA-Z0-9#+]+)", match.lower())
            ), filter(lambda tag: tag, contained_tags)
        )
    ))[:3]
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

def get_page_links(page):
    paginator = page.paginator
    page_links = list(paginator.page_range)
    total_pages = paginator.num_pages
    if total_pages >= 5:
        if page.number == page_links[-1] or page.number == page_links[-2]:
            return [paginator.page(n) for n in page_links[-5:]]
        elif page.number < 3:
            return [paginator.page(n) for n in page_links[:5]]
        page_index = page_links.index(page.number)
        return [paginator.page(n) for n in page_links[page_index - 2:page_index + 3]]
    return [paginator.page(n) for n in range(1, total_pages + 1)]
