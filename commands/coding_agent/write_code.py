# def write_code(page, code):
#     try:
#         page.evaluate(
#             """
#             code => {
#                 monaco.editor
#                     .getModels()[0]
#                     .setValue(code)
#             }
#             """,
#             code
#         )

#         speak("Code written")

#         return True

#     except Exception as e:

#         speak(f"Write Error: {e}")

#         return False
def write_code(page, code):
    try:
        page.wait_for_selector('.monaco-editor')

        page.evaluate(
            """
            code => {
                const editor = monaco.editor.getModels()[0];
                editor.setValue(code);
            }
            """,
            code
        )

        speak("Code written")

        return True

    except Exception as e:
        speak(f"Write Error: {e}")
        return False