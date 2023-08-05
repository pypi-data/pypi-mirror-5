from HtmlToWord.elements.Base import *
from win32com.client import constants
from HtmlToWord import groups


class Break(ChildlessElement):
    """
    I'm a really annoying element who gets in the way of things. I sometimes have an effect and I sometimes don't.
    If I'm in a Paragraph I cause the paragraph to change its style
    If I'm in a ListElement I mess things up so I am excluded from the party :(

    I still have a few bugs to do with me being nested in tags and then those tags being in paragraphs and lists,
    but screw it.
    """
    def EndRender(self):
        self.selection.TypeParagraph()


class Div(BaseElement):
    pass


class Span(IgnoredElement):
    pass


class Image(ChildlessElement):
    def StartRender(self):
        url = self.GetAttrs()["src"]
        caption = self.GetAttrs()["alt"]
        self.Image = self.selection.InlineShapes.AddPicture(FileName=url)
        with self.With(self.Image.Borders) as Borders:
            Borders.OutsideLineStyle = constants.wdLineStyleSingle
            Borders.OutsideColor = constants.wdColorPaleBlue
        self.selection.TypeParagraph()

        if caption:
            style = self.selection.Range.Style
            self.selection.Range.Style = self.GetDocument().Styles("caption")
            self.selection.TypeText(caption)


class HyperLink(BaseElement):
    # Formatting tags don't work well inside hyperlinks. Ignore them.
    IgnoredChildren = groups.FORMAT_TAGS

    def StartRender(self):
        self.start_range = self.selection.Range.End

    def EndRender(self):
        href = self.GetAttrs()["href"]
        if href:
            document_range = self.GetDocument().Range(Start=self.start_range,
                                                      End=self.selection.Range.End)

            self.GetDocument().Hyperlinks.Add(Anchor=document_range,
                                              Address=href)