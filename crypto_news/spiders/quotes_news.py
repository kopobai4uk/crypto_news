import requests

headers = {
    'authority': 'conpletus.cointelegraph.com',
    'accept': '*/*',
    'dnt': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://cointelegraph.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://cointelegraph.com/tags/bitcoin',
    'accept-language': 'uk-UA,uk;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6',
}

data = '{"operationName":"TagPagePostsQuery","variables":{"slug":"ethereum","order":"postPublishedTime","offset":15,"length":15,"short":"en","cacheTimeInMS":300000},"query":"query TagPagePostsQuery($short: String, $slug: String!, $order: String, $offset: Int!, $length: Int!) {  locale(short: $short) {    tag(slug: $slug) {      cacheKey      id      posts(order: $order, offset: $offset, length: $length) {        data {          cacheKey          id          slug          views          postTranslate {            cacheKey          id            title           avatar           published           publishedHumanFormat          leadText            __typename        }          category {            cacheKey            id           __typename          }          author {            cacheKey            id            slug           authorTranslates {              cacheKey              id              name             __typename            }           __typename          }          postBadge {           cacheKey           id            label         postBadgeTranslates {              cacheKey              id              title             __typename            }            __typename          }          showShares          showStats          __typename        }    postsCount        __typename      }     __typename    }    __typename  }}"}'

response = requests.post('https://conpletus.cointelegraph.com/v1/', headers=headers, data=data)
print(response.json())
