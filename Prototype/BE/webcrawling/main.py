from Prototype.BE.webcrawling.crawler import BlogCrawler

# [데이터 셋에 필요한 것] <3000개>
# [링크, 본문, 모든 사진 링크]

if __name__ == "__main__":
    query = "맛집"
    BC = BlogCrawler(query)
    BC.get_data_with_query()