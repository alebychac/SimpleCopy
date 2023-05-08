import os
import time
import shutil
import playsound
from PySide6 import QtWidgets, QtGui, QtCore

import ctypes

# Set some variables for the application
enterprise = "bychac_solutions"
product = "VSNCopy"
subproduct = "SITVC"
version = "1.0"

class CopyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Set the application ID and name
        self.app_id = f'{enterprise}.{product}.{subproduct}.{version}' # arbitrary strin
        self.app_name = f'{product}'

        # Set the taskbar icon (for Windows)
        icon_path = "assets/sitvc.ico"
        logo_icon = QtGui.QIcon()
        logo_icon.addFile(icon_path, QtCore.QSize(16,16))
        logo_icon.addFile(icon_path, QtCore.QSize(24,24))
        logo_icon.addFile(icon_path, QtCore.QSize(32,32))
        logo_icon.addFile(icon_path, QtCore.QSize(48,48))
        logo_icon.addFile(icon_path, QtCore.QSize(256,256))        
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.app_id)

        self.icon = logo_icon
        self.app = app

        self.setWindowIcon(self.icon)        

        self.window_title = f'{product}'

        self.source_path = ""
        self.current_element_to_copy = ""
        self.dest_path = ""
        self.file_name = ""
        self.file_size = 0
        self.bytes_copied = 0

        dirs_to_copy = ["D:/Documents", "C:/Temp", "E:/Backups"]

        # Set the window title
        self.setWindowTitle("VSNCopy")

        # Set the window position and size
        self.setGeometry(100, 100, 400, 100)



        self.source_label = QtWidgets.QLabel("Arrastra y suelta un archivo(s) o carpeta(s) aquí")
        self.dest_combo = QtWidgets.QComboBox()
        self.dest_combo.addItems(dirs_to_copy)
        self.copy_button = QtWidgets.QPushButton("Copiar")
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setValue(0)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.source_label)
        layout.addWidget(self.dest_combo)
        layout.addWidget(self.copy_button)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

        self.setAcceptDrops(True)
        self.copy_button.clicked.connect(self.copy_file)

        # Center the window on the screen
        self.center_on_screen()

    def center_on_screen(self):
        # Get the primary screen geometry
        screen = QtWidgets.QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Set the window geometry
        window_geometry = self.geometry()
        x = int((screen_geometry.width() - window_geometry.width()) / 2)
        y = int((screen_geometry.height() - window_geometry.height()) / 2)
        self.setGeometry(x, y, window_geometry.width(), window_geometry.height())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            self.source_paths = file_paths
            self.file_names = [os.path.basename(file_path) for file_path in file_paths]
            self.file_sizes = [os.path.getsize(file_path) for file_path in file_paths]
            self.source_label.setText(", ".join(self.file_names))
            event.accept()
        else:
            event.ignore()
    
    def copy_file(self):
        if not self.source_paths:
            return

        for i, source_path in enumerate(self.source_paths):
            self.current_element_to_copy = source_path
            self.source_path = source_path
            self.dest_path = os.path.join(self.dest_combo.currentText(), self.file_names[i])
            self.file_name = self.file_names[i]
            self.file_size = self.file_sizes[i]

            if os.path.exists(self.dest_path):
                result = self.handle_conflict(self.dest_path)
                if result == "Cancelar":
                    continue
                elif result == "Sobrescribir":
                    if os.path.isdir(self.dest_path):
                        shutil.rmtree(self.dest_path)
                    else:
                        os.remove(self.dest_path)
                elif result == "Combinar":
                    if os.path.isdir(source_path):
                        self.combine_folders(source_path, self.dest_path)
                elif result == "Mantener ambos":
                    self.dest_path = self.get_unique_name(self.dest_path, add_number=False)

            try:
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, self.dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_path, self.dest_path, follow_symlinks=True)
            except Exception as e:
                print(e)
                playsound.playsound("assets/error.mp3")
                return

        playsound.playsound("assets/notification.mp3")

    def combine_folders(self, source_path, dest_path):
        for item in os.listdir(source_path):
            src_item_path = os.path.join(source_path, item)
            dst_item_path = os.path.join(dest_path, item)
            
            self.current_element_to_copy = src_item_path
            
            if os.path.exists(dst_item_path):
                result = self.handle_conflict(dst_item_path)
                if result == "Cancelar":
                    return
                elif result == "Sobrescribir":
                    if os.path.isdir(dst_item_path):
                        shutil.rmtree(dst_item_path)
                    else:
                        os.remove(dst_item_path)
                elif result == "Combinar":
                    if os.path.isdir(src_item_path):
                        self.combine_folders(src_item_path, dst_item_path)
                elif result == "Mantener ambos":
                    dst_item_path = self.get_unique_name(dst_item_path, add_number=False)

            try:
                if os.path.isdir(src_item_path):
                    shutil.copytree(src_item_path, dst_item_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_item_path, dst_item_path, follow_symlinks=True)
            except Exception as e:
                print(e)
                playsound.playsound("error.mp3")
                return

    def handle_conflict(self, dest_path):        
        choice_list = ["Cancelar", "Sobrescribir", "Mantener ambos"]
        if os.path.isdir(self.current_element_to_copy):
            choice_list = ["Cancelar", "Sobrescribir", "Combinar", "Mantener ambos"]
        
        # Get the size and last modification date of the file in the destination folder
        dest_size = os.path.getsize(dest_path)
        dest_modified_time = os.path.getmtime(dest_path)
        dest_modified_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dest_modified_time))
        src_size = os.path.getsize(self.current_element_to_copy)
        src_modified_time = os.path.getmtime(self.current_element_to_copy)
        src_modified_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(src_modified_time))
        
        file_or_folder = "El archivo"        
        if os.path.isdir(dest_path):            
            file_or_folder = "La carpeta"
        message = f"{file_or_folder} '{os.path.basename(dest_path)}' ya existe.\n\n" \
                f"Origen: {self.current_element_to_copy}\n" \
                f"Tamaño del origen: {src_size} bytes\n" \
                f"Última modificación del origen: {src_modified_time_str}\n\n" \
                f"Destino: {dest_path}\n" \
                f"Tamaño en el destino: {dest_size} bytes\n" \
                f"Última modificación en el destino: {dest_modified_time_str}\n\n" \
                f"¿Qué desea hacer?"
                
        msg_box = QtWidgets.QMessageBox()
        msg_box.setText(message)
        msg_box.setWindowTitle("Conflicto")
        for choice in choice_list:
            msg_box.addButton(choice, QtWidgets.QMessageBox.ActionRole)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        result = msg_box.exec_()
        return choice_list[result]           
   
    def get_unique_name(self, path, add_number=False):
        base_path, ext = os.path.splitext(path)
        if add_number:
            i = 1
            new_path = f"{base_path} ({i}){ext}"
            while os.path.exists(new_path):
                i += 1
                new_path = f"{base_path} ({i}){ext}"
        else:
            # Get current date and time in the format year-month-day--hour-minutes-seconds
            current_time = time.strftime('%Y-%m-%d a las %H-%M-%S', time.localtime())
            new_path = f"{base_path}--copiado el {current_time}{ext}"
            while os.path.exists(new_path):
                current_time = time.strftime('%Y-%m-%d at %H-%M-%S', time.localtime())
                new_path = f"{base_path}--copiado el {current_time}{ext}"
        return new_path
            
if __name__ == '__main__':
    # Create the application object
    app = QtWidgets.QApplication([])

    # Create and show the main window
    window = CopyWindow()
    window.show()

    # Run the event loop
    app.exec_()