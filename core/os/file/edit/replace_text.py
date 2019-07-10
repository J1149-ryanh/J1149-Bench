# -*- coding: utf-8 -*-

import os
import shutil 


class LineInFile:
    
    def __init__(self, path=None, line=None, line_num=None):
        self.path = path
        self.line = line
        self.line_num = line_num
        
    def reset(self):
        self.path = None
        self.line = None
        self.line_num = None
        
    def search_text_in_file(self, text, path):
        with open(path, 'r') as fyle:
            try:
                for line_num, line in enumerate(fyle):
                    if text.lower() in line.lower():
                        self.path = path
                        self.line = line
                        self.line_num = line_num
                        yield self
                        self.reset()
            except UnicodeDecodeError as e:
                print(e)
                
    def replace_text_in_file(self, text, replace_with, path):
        count = 0
        lines = []
        with open(path, 'r') as fyle:
            try:
                for line_num, line in enumerate(fyle):
                    if text.lower() in line.lower():
                        count += 1
                        beg = line.lower().index(text.lower())
                        end = beg+len(text)
                        s = line[beg:end]
                        new_line = line.replace(s, replace_with)
                        lines.append(new_line)
                        print(line, beg, end, s,new_line)
                    else:
                        lines.append(line)
            except UnicodeDecodeError as e:
                print(e)
                return 0
            
        if count == 0:
            return 0
        
        with open(path, 'w') as fyle:
            for line in lines:
                fyle.write(line)
        return count
        
    def __str__(self):
        if self.line is None:
            return "Line not found"
        return "{0} (l:{1}): {2}".format(self.path, self.line_num, self.line)


def in_exclude_dirs(root, exclude_dirs):
    for exclude_dir in exclude_dirs:
        if exclude_dir in root:
            return True
    return False


def search_for_text(text, dirpath, exclude_dirs=[]):
    lif = LineInFile()
    for root, dirnames, filenames in os.walk(dirpath):
        
        if in_exclude_dirs(root, exclude_dirs):
            continue
        
        for filename in filenames:
            path = os.path.join(root, filename)
            for new_lif in lif.search_text_in_file(text, path):
                print(new_lif)
    

def replace_text(text, replace_with, dirpath, dirpath_clone, exclude_dirs=[]):
    lif = LineInFile()
    if os.path.exists(dirpath_clone):
        shutil.rmtree(dirpath_clone)
    shutil.copytree(dirpath, dirpath_clone)
    for root, dirnames, filenames in os.walk(dirpath_clone):
        
        if in_exclude_dirs(root, exclude_dirs):
            continue
        
        for filename in filenames:
            path = os.path.join(root, filename)
            count = lif.replace_text_in_file(text, replace_with, path)
            if count < 1:
                continue
            rplc_cnt = '{0} : {1} instance(s) replaced'.format(path, count)
            print(rplc_cnt)
                
                
if __name__ == '__main__':
    import os

    def example_usage(text, replace_with, exclude_dirs):
        git_url = r'https://github.com/J1149-ryanh/j1149.github.io.git'
        git_dirname = os.path.basename(git_url)[:-4]
        tmp_dir = os.path.expanduser('~/tmp')
        git_path = os.path.join(tmp_dir, git_dirname)

        if not os.path.exists(git_path):
            import git
            repo = git.Repo.clone_from(git_url, git_path, branch='design4')
        git_dir_clone = git_path + '.clone'

        replace_text(text, replace_with, git_path, git_dir_clone, exclude_dirs)

    exclude_dirs = [r'\.git', r'\.github', r'\.sass-cache', '_includes',
                    '_layouts', '_sass', '_site']
    text = 'pai-cli'
    replace_with = "paicoin-cli"
    example_usage(text, replace_with, exclude_dirs)
