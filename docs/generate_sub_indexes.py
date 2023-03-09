
"""
Generates sub indexes of files such as the .md files in the top level of this repo.

Note - you will have to add the indexes generated to index.rst manually.
"""

import os
import shutil

TOP_LEVEL_FILES_LINK_DIR = "top_level_md_files"
SOURCE_MEWBOT_DIR = "source_mewbot"
SOURCE_EXAMPLES_DIR = "source_examples"

TOP_LEVEL_FILES_NEED_TITLE = {
    "code_of_conduct.md": False
}


def generate_top_level_md_files_index() -> None:
    """
    Generate include objects for the .md files at the top level of the directory.

    The top level files are included via bridge files
    These are rst files in the top level which include the md files themselves in the directory
    root.
    The reason it was done this way was because you _cannot_ directly include an object into the
    contents tree, but you _can_ include a rst document which include the entire, translated, md
    file.

    Some of these files do not include things which are recognizable titles.
    So titles need to be added to some files. But not others.
    This is what the `TOP_LEVEL_FILES_NEED_TITLE` constant is for - do the generated files need
    a title?
    """
    top_level_files = os.listdir("..")

    if os.path.exists(TOP_LEVEL_FILES_LINK_DIR):
        shutil.rmtree(TOP_LEVEL_FILES_LINK_DIR)
    os.mkdir(TOP_LEVEL_FILES_LINK_DIR)

    valid_index_files: list[str] = []
    for file_name in top_level_files:

        if os.path.splitext(file_name)[1] != ".md":
            continue

        file_name_token = os.path.splitext(file_name)[0]
        ref_file_path = os.path.join(
            TOP_LEVEL_FILES_LINK_DIR, f"main_{file_name_token.lower()}.rst"
        )

        if os.path.exists(ref_file_path):
            os.unlink(ref_file_path)

        file_title_status = TOP_LEVEL_FILES_NEED_TITLE.get(file_name.lower(), True)

        fn_title_emph_str = "=" * len(file_name)
        with open(ref_file_path, "w") as fn_ref_file:
            if file_title_status:
                fn_ref_file.write(f"""..
    Note - this is an auto generated file! All changes may be randomly lost!
    
{file_name}
{fn_title_emph_str}

.. mdinclude:: ../../{file_name}
                """)

            else:
                fn_ref_file.write(f"""..
    Note - this is an auto generated file! All changes may be randomly lost!

.. mdinclude:: ../../{file_name}
                            """)

        valid_index_files.append(os.path.splitext(ref_file_path)[0])

    # Process valid_index_files into an OS agnostic form
    new_valid_index_files: list[str] = []
    for file_path in valid_index_files:
        file_tokens = file_path.split(os.sep)
        new_valid_index_files.append("/".join(file_tokens))

    valid_index_files = new_valid_index_files

    index_str = "   " + "\n   ".join(valid_index_files)

    with open("main_files_index.rst", "w") as main_files_index:
        main_files_index.write(f"""
        
.. toctree::
   :maxdepth: 4
   :caption: Top Level MD files:

{index_str}

""")


def generate_source_index(src_folder: str) -> None:

    src_dir_paths: list[str] = []
    for file_name in os.listdir(src_folder):
        src_dir_paths.append(src_folder + "/" + os.path.splitext(file_name)[0])

    src_files_index_file = f"{src_folder}_index.rst"

    if os.path.exists(src_files_index_file):
        os.unlink(src_files_index_file)

    index_str = "   " + "\n   ".join(src_dir_paths)

    with open(src_files_index_file, "w") as src_index_file:
        src_index_file.write(f"""

.. toctree::
   :maxdepth: 4
   :caption: {src_folder} file index:

{index_str}

    """)


if __name__ == "__main__":

    generate_top_level_md_files_index()
    generate_source_index(src_folder=SOURCE_MEWBOT_DIR)
