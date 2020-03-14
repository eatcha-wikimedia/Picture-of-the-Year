import re
import time
import pywikibot
from pywikibot import pagegenerators

# To calculate execution time, if very large TODO: multiprocessing support
start_time = time.time()


def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding.'''
    # https://stackoverflow.com/questions/783897/truncating-floats-in-python , out put is string
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

def rows_maker():
    '''Creates list rows of the wiki-table by parsing data from wikitext.'''
    candidates_text = ''
    total_candidates = 0
    total_votes = 0
    voters_array = []
    gen1 = pagegenerators.UserContributionsGenerator("Zhuyifei1999", namespaces=4)
    for page in gen1:
        candidate_name = page.title()
        if candidate_name.startswith('Commons:Picture of the Year/2019/R1/v/') and not candidate_name.endswith('.webm'):
            total_candidates = total_candidates + 1
            print(total_candidates , ' - ' , candidate_name)
            candidate_page = pywikibot.Page(SITE, candidate_name)
            candidate_voters_list = list(candidate_page.contributors())
            try:
                candidate_page_text = candidate_page.get(get_redirect=True, force=True)
            except:
                continue
            for voter in candidate_voters_list:
                if voter not in voters_array:
                    voters_array.append(voter)
            Votes = len(re.findall(r"#\s", candidate_page_text))
            File_Name = 'File:'+re.search(r"Commons:Picture of the Year/2019/R1/v/(.*)", candidate_name).group(1)
            File_Page =  pywikibot.Page(SITE, File_Name)
            history = File_Page.getVersionHistory(reverseOrder=True, total=1)
            if not history:
                File_Uploader = "Unknown"
            else:
                File_Uploader = "[[User:%s|%s]]" % (history[0][2], history[0][2])
                history = candidate_page.getVersionHistory(total=1)
                last_diff = "[https://commons.wikimedia.org/w/index.php?diff=%s (show-diff)]" % history[0][0]
                last_editor = "[[User:%s|%s]]" % (history[0][2], history[0][2])
            
            File_Page =  pywikibot.FilePage(SITE, File_Name)
            usage = File_Page.usingPages()
            for use in usage:
                use=use.title()
                if use.startswith('Commons:Featured picture candidates/File:') or use.startswith('Commons:Featured picture candidates/Set'):
                    fp_nom_page_name = use
                else:
                    Nominator = 'Unknown'
            if fp_nom_page_name != 'Unknown':
                fp_nom_page = pywikibot.Page(SITE, fp_nom_page_name)
                history = fp_nom_page.getVersionHistory(reverseOrder=True, total=1)
                if not history:
                    Nominator = 'Unknown'
                else:
                    Nominator = "[[User:%s|%s]]" % (history[0][2], history[0][2])

            candidate_Row = """\n| [[:%s]]\n| [[%s|120px]]\n| %s\n| %s\n| [[%s]]\n| %d\n| %s - %s\n|- style="background:  #ffffff; color:  #000000  ;" """ % (
                File_Name, 
                File_Name, 
                File_Uploader, 
                Nominator, 
                candidate_name, 
                Votes, 
                last_editor, 
                last_diff,
                )
            candidates_text = candidates_text + candidate_Row
            total_votes = total_votes + Votes

    EditSummary = "Updating results - POTY 2019"
    total_voters = (len(voters_array))
    average_votes_by_a_user = (total_votes/total_voters)
    a_mean = total_votes/total_candidates
    new_text = ( """Disclaimer : These results are not endorsed by Picture of the Year 2019 Committee. See bottom of this page for more info."""
    + """\n<div style="border: 3px solid  #000000 ;">\n{| class="wikitable sortable"\n|-"""
    + """\n|+ width=120px  | [[File:POTY_barnstar.svg|left|link=|80px|alt=POTY logo]]<div style="background-color:  white ; border: 3px solid  ##000000; margin: 1px; padding: 0px;">"""
    + """\n<div style="font-size: 16px; text-align: center;"> """
    + """Live POTY Results - Powered by [[User:EatchaBot|EatchaBot]]<br>[[File:Bert2 transp 5B5B5B cont 150ms.gif]]<br> <span style="font-size: 14px;"> """
    + """Last Updated at : {{subst:#time: H:i:s}} UTC &nbsp;&nbsp;&nbsp; Next update scheduled at : {{subst:#time: H:i:s| + 31 minutes}} UTC &nbsp;&nbsp;&nbsp; Click on ↕️ to sort the columns."""
    + """<br> Total number of votes : %s &nbsp;&nbsp;&nbsp; Total Candidates : %s &nbsp;&nbsp;&nbsp; Average votes per Candidate (x̅) : %s <br>""" % (
        str(total_votes),
        str(total_candidates),
        truncate(a_mean, 3),
        )
    + """Total unique voters : %s &nbsp;&nbsp;&nbsp; Average votes by a single voter (x̅): %s </span></div> """ % (
        str(total_voters),
        truncate(average_votes_by_a_user, 3),
        )
    + """\n</div>\n|-
! style="background: #000000; color:   #ffffff ;" | '''File Name ↕️'''
! style="background: #000000; color:   #ffffff ;" | '''File Thumbnail ↕️'''
! style="background: #000000; color:   #ffffff ;" | '''Uploader ↕️'''
! style="background: #000000; color:   #ffffff ;" | '''FP Nominator ↕️ '''
! style="background: #000000; color:   #ffffff ;" | '''Candidate Page ↕️'''
! style="background: #000000; color:   #ffffff ;" | '''{{s|Votes}} ↕️'''
! style="background: #000000; color:   #ffffff ;" | '''Recent voter ↕️'''
|- style="background:  #ffffff; color:  #000000  ;"\n"""
    + candidates_text 
    + "\n|}</div>\n'''Disclaimer''' : These results are not endorsed by Picture of the Year 2019 Committee. <br> Use at Your Own Risk. "
    + "We provide the material available through this Service for informational purposes only. "
    + "We try to ensure that information we post to this Service is both timely and accurate, and that the services offered are reliable. "
    + "Despite our efforts, however, content or services on this Service may, from time to time, contain errors."
    )

    # Adding this at the bottom is best practice in all case where we just wanna update the page, min edit-conflit
    live_page = pywikibot.Page(SITE, 'User:Eatcha/2019/Picture-of-the-Year-Round-1-Real-Time-Results')
    try:
        live_page_current_text = live_page.get(get_redirect=True, force=True)
    except pywikibot.exceptions.NoPage:
        live_page_current_text = ''
    if new_text == live_page_current_text:
        print("No changes made")
        return
    else:
        pywikibot.showDiff(live_page_current_text, new_text)
        try:
            live_page.put(new_text, summary=EditSummary, watch=False, minor=False)
        except pywikibot.LockedPage as error:
            print("Page is locked '%s'." % error)
            return

def main():
    global SITE
    SITE = pywikibot.Site()

    if not SITE.logged_in():
        SITE.login()

    rows_maker()
    print("---Execution time: %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
  try:
    main()
  finally:
    pywikibot.stopme()
