import pathlib
import uuid

from ebooklib import epub

class Txt2Epub:
    def __init__(
        self,
        book_identifier=None,
        book_title=None,
        book_author=None,
        book_language=None,
    ):
        self.book_identifier = book_identifier or str(uuid.uuid4())
        self.book_title = book_title
        self.book_author = book_author
        self.book_language = book_language

    def create_epub(self, input_file: pathlib.Path, cover_image_file, output_file: pathlib.Path = None, chapter_identifier: str = None):
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read()

        # create new EPUB book
        book = epub.EpubBook()

        # set metadata
        book.set_identifier(self.book_identifier)
        book.set_title(self.book_title)
        book.add_author(self.book_author or "Unknown")

        if cover_image_file:
            cover_image_name = cover_image_file.name
            cover_image_content = open(cover_image_file, 'rb').read()
            book.set_cover(cover_image_name, cover_image_content)

        # create chapters
        if chapter_identifier:
            # split text into chapters
            chapters = text.split(chapter_identifier) # e.g. "##"

            chapters_title = []
            
            for i in chapters:
                title_end_loc = i.find('\n') 
                chapters_title.append(i[:title_end_loc])

            chapters.pop(0)
            chapters_title.pop(0)
            
            spine = ["nav"]
            toc = []
            for chapter_id, chapter_content_full in enumerate(chapters):
                chapter_lines = chapter_content_full.split("\n")
                chapter_title = chapter_lines[0]
                chapter_content = chapter_lines[1:]

                # write chapter title and contents
                chapter = epub.EpubHtml(
                    title=chapter_title,
                    file_name="chap_{:03d}.xhtml".format(chapter_id + 1),
                    lang="zh-Hans",
                )
                chapter.content = "<h1>{}</h1>{}".format(
                    chapter_title,
                    "".join("<p>{}</p>".format(line) for line in chapter_content),
                )

                # add chapter to the book and TOC
                book.add_item(chapter)
                spine.append(chapter)
                toc.append(chapter)

            # update book spine and TOC
            book.spine = spine
            book.toc = toc

            # add navigation files
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
        
        else:
            spine = ["nav"]
            toc = []

            # write text content
            chapter = (epub.EpubHtml(
                uid="content",
                file_name="content.xhtml",
                lang="zh-Hans",
                content="".join("<p>{}</p>".format(line) for line in text.split("\n")),
            ))

            book.add_item(chapter)
            spine.append(chapter)
            # toc.append(chapter)
            toc = [epub.Link(chapter.file_name, 'Content', chapter.id)]

            # update book spine and TOC
            book.spine = spine
            book.toc = toc

            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())

        # generate new file path if not specified
        if output_file is None:
            output_file = input_file.with_suffix(".epub")

        # create EPUB file
        epub.write_epub(output_file, book)

