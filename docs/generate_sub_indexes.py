
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
    "code_of_conduct.md": False,
    "contributing.md": False,
    "contributors.md": False,
    "readme.md": False
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

    assert "README.md" in top_level_files, f"README.md not found in the projects root! {top_level_files}"

    # Shuffle README.md to the front of the list, so it'll be displayed at the top
    top_level_files.remove("README.md")
    top_level_files = ["README.md", ] + top_level_files

    if os.path.exists(TOP_LEVEL_FILES_LINK_DIR):
        shutil.rmtree(TOP_LEVEL_FILES_LINK_DIR)
    os.mkdir(TOP_LEVEL_FILES_LINK_DIR)

    valid_index_files: list[str] = []
    for file_name in top_level_files:

        # Also copy any images from the top level into the link dir
        if os.path.splitext(file_name)[1].lower() in (".svg", ".tff", ".jpg"):

            new_image_path = os.path.join(TOP_LEVEL_FILES_LINK_DIR, file_name)
            shutil.copy(os.path.join("..", file_name), new_image_path)

        if os.path.splitext(file_name)[1].lower() != ".md":
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
    """
    Assists auto-generation of documentation from doc strings of entire modules.

    sphinx has an inbuilt script for iteratively generating documentation from the doc strings of
    entire modules.
    However, it doesn't have a good means of generating index files for this auto-generated files
    so you can include them more easily in the docs.
    This function generates that index file, which can then be included in the toc for the master
    index file.
    :param src_folder:
    :return:
    """

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


def generate_docs_folder_index(docs_folder: str) -> None:
    """
    Generates an index file so an entire docs tree (e.g. design-docs) can be included in the toc.

    :param docs_folder:
    :return:
    """
    valid_file_paths = []
    for root, dirs, files in os.walk(docs_folder):
        for file_name in files:
            if os.path.splitext(file_name)[1].lower() != ".md":
                continue

            valid_file_paths.append(os.path.join(root, file_name))

    # Process valid_index_files into an OS agnostic form
    files_in_index = ["/".join(path.split(os.sep)) for path in valid_file_paths]
    index_str = "   " + "\n   ".join(files_in_index)

    # Caption string which will be used to name this toc
    # Take each folder name segment, put it in title case.
    name = " ".join(_.title() for _ in docs_folder.split("-"))

    # Gen the index name and remove it if it exists already
    index_file_name = f"{docs_folder}-index.rst"
    if os.path.exists(index_file_name):
        os.unlink(index_file_name)

    # Write the index file out
    with open(index_file_name, "w") as main_files_index:
        main_files_index.write(f"""

..
  NOTE - THIS IS AN AUTO-GENERATED FILE - CHANGES MADE HERE WILL NOT PERSIST!

.. toctree::
   :maxdepth: 4
   :caption: {name}:

{index_str}

    """)


if __name__ == "__main__":

    generate_top_level_md_files_index()
    generate_source_index(src_folder=SOURCE_MEWBOT_DIR)
    generate_source_index(src_folder=SOURCE_EXAMPLES_DIR)
    generate_docs_folder_index("design-docs")
    generate_docs_folder_index("dev-docs")
