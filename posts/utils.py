
import re
from functools import reduce

def retrieve_exact_phrases(user, tags, title, string):
    '''Searches for phrases not associated with a title, user, or tag'''

    phrases = string
    if user:
        leading_zeros_pattern = re.compile(r"(?<=user:)0*")
        zeros = leading_zeros_pattern.search(string)[0]
        phrases = re.sub(f"user:{zeros}{user}", "", phrases)
    if title:
        phrases = re.sub(f"title:{title}", "", phrases)
    if tags:
        phrases = re.sub(r"(\[)\1*[^\[\]].*(\])\2*", "", phrases)
    phrases = re.sub(r"\s+", " ", phrases).lower().strip(" ").split(" ")
    if phrases:
        return phrases
    return None

def retrieve_query_title(string):
    '''Extracts the title of a performed search query'''
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
    '''Clean each tag of unaccepted characters'''
    contained_tags = list(map(lambda cleaned_match: "" if not cleaned_match else reduce(
        lambda acc, cur: (
            acc + "" if cur == "-" and acc[-1] == "-" else acc + cur
        ), cleaned_match
    ), map(
        lambda match: re.sub(r"[*!$&'\"()%*,/:;?^=@\[\]<>_`~{}|\s\\]", "", match[0])
        , re.finditer(r"(?<=\[)[^\[\]]+(?=\])", string)
    )))[:3]
    if all(not tag for tag in contained_tags):
        return None
    returned_tags = list(map(
        lambda tag: clean_tag_version(tag), filter(
            lambda tag: tag, map(
                lambda tag: tag.strip("-").lstrip("#+."), contained_tags
            )
        )
    ))
    return returned_tags

def clean_tag_version(tag):
    '''Clean the version provided of a given tag'''
    tag_version_match = re.search(r"\d+(\.+\d+)*", tag)
    if tag_version_match:
        user_provided_version = tag_version_match.start()
        version = reduce(
            lambda string, char: (
                string + "" if char == "." and string[-1] == "." else string + char
            ), tag[user_provided_version:]
        )
        tag = f"{tag_version_match.string[:user_provided_version]}{version}".lower()
    tag = re.sub(r"(?<=[A-Za-z])?\.*(?=[A-Za-z])", "", tag).lower()
    return tag

def retrieve_query_user_id(string):
    '''Returns the id of a given registered user'''
    user_id_search = re.compile(r"(?<=user:)(\d+)")
    searching_by_user = user_id_search.search(string)
    if searching_by_user:
        id = searching_by_user[0].lstrip("0")
        return int(id)
    return None

def resolve_search_query(string):
    search_query_title = retrieve_query_title(string)
    search_tags = retrieve_query_tags(string)
    search_user = retrieve_query_user_id(string)
    phrases = retrieve_exact_phrases(search_user, search_tags, search_query_title, string)
    return {
        'title': search_query_title,
        'tags': search_tags,
        'user': search_user,
        'phrases': phrases
    }

def get_page_links(page):
    '''Returns a list of page links'''
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
