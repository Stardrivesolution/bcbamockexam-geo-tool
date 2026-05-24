from app.services.extractor import HtmlExtractor


def test_extract_basic_page_data():
    html = """
    <html>
      <head>
        <title>Test Page</title>
        <meta name="description" content="A useful test page">
        <link rel="canonical" href="/canonical">
        <script type="application/ld+json">{"@type":"Article","headline":"Test"}</script>
      </head>
      <body>
        <main>
          <h1>Main Topic</h1>
          <h2>Question</h2>
          <p>This page answers a useful question.</p>
          <a href="/about">About</a>
          <img src="/hero.png" alt="Hero image">
        </main>
      </body>
    </html>
    """

    page = HtmlExtractor().extract(html, "https://example.com/page")

    assert page.title == "Test Page"
    assert page.meta_description == "A useful test page"
    assert page.h1_count == 1
    assert page.headings[0].text == "Main Topic"
    assert page.links[0].href == "https://example.com/about"
    assert page.images[0].alt == "Hero image"
    assert page.json_ld[0]["@type"] == "Article"
