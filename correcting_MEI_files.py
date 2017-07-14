import os, sys
sys.path.append('/Users/yaolongju/Documents/Projects/libmei/python')
import pymei


def modifying_MEI():
    """
    Remove 'breve' attribute which is not supported by jsymbolic2
    :return:
    """
    for id, fn in enumerate(os.listdir('./downloaded_files/')):
        if (fn[-3:] == 'mei' and fn.find('NEW') == -1):
            print(fn)
            doc = pymei.documentFromFile('./downloaded_files/' + fn).getMeiDocument()
            notes = doc.getElementsByName('note')
            for i, note in enumerate(notes):
                dur = note.getAttribute('dur')
                if(dur.getValue() == 'breve'):  # copy the note, change the duration into whole and tie them together
                    layer = note.getAncestor('layer')
                    note.addAttribute('dur', '1')
                    newnote = pymei.MeiElement('note')
                    newnote.addAttribute('pname', note.getAttribute('pname').getValue())
                    newnote.addAttribute('oct', note.getAttribute('oct').getValue())
                    newnote.addAttribute('dur', '1')
                    dots = note.getAttribute('dots')
                    if(dots != None):
                        newnote.addAttribute('dots', dots.getValue())
                    if(i + 1 < len(notes)):
                        layer.addChildBefore(note, newnote)
                    else:
                        layer.addChild(newnote)
                    id1 = note.getId()
                    newnote.setId(id1 + 'copy')
                    id2 = newnote.getId()
                    measure = note.getAncestor('measure')
                    tie = pymei.MeiElement('tie')
                    tie.addAttribute('startid', id1)
                    tie.addAttribute('endid', id2)
                    measure.addChild(tie)
            rests = doc.getElementsByName("rest")
            for i, rest in enumerate(rests):  # rest needs to fix as well
                dur = rest.getAttribute('dur')
                if (dur != None):
                    if (dur.getValue() == 'breve'):  # copy the note, change the duration into whole and tie them together
                        layer = rest.getAncestor('layer')
                        rest.addAttribute('dur', '1')
                        newrest = pymei.MeiElement('rest')
                        newrest.addAttribute('dur', '1')
                        dots = rest.getAttribute('dots')
                        if (dots != None):
                            newrest.addAttribute('dots', dots.getValue())
                        if(i + 1 < len(rests)):
                            layer.addChildBefore(rest, newrest)
                        else:
                            layer.addChild(newrest)
                        id1 = rest.getId()
                        newrest.setId(id1 + 'copy')
                        id2 = newrest.getId()
                        measure = rest.getAncestor('measure')
                        tie = pymei.MeiElement('tie')
                        tie.addAttribute('startid', id1)
                        tie.addAttribute('endid', id2)
                        measure.addChild(tie)
            pymei.documentToFile(doc, './downloaded_files/' + fn[:-4] + 'NEW' + '.mei')



if __name__ == "__main__":
    modifying_MEI()

