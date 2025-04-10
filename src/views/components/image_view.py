"""
테니스 공 추적기 애플리케이션의 이미지 뷰 컴포넌트.

이미지를 표시하고 확대/축소, 패닝 등의 기능을 제공하는 UI 컴포넌트입니다.
"""

import cv2
import numpy as np
from PySide6.QtCore import Qt, QPoint, Signal, QSize
from PySide6.QtGui import QImage, QPixmap, QCursor, QPainter
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QMenu, QApplication

from src.models.app_state import AppState
from src.constants.ui_constants import DARK_BACKGROUND_STYLE


class ImageView(QWidget):
    """
    이미지 표시 및 조작을 위한 UI 컴포넌트.
    
    이미지 표시, 확대/축소, 패닝 기능을 제공합니다.
    """
    
    # 확대/축소 제한 및 비율
    MIN_ZOOM = 0.1
    MAX_ZOOM = 10.0
    ZOOM_FACTOR = 1.2
    
    # Signal emitted when image is clicked
    clicked = Signal(int, int)
    
    def __init__(self, parent=None):
        """
        ImageView 컴포넌트 초기화
        
        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        
        # AppState 인스턴스 가져오기
        self.app_state = AppState.get_instance()
        
        # 내부 상태 초기화
        self.pixmap = QPixmap()
        self.zoom_level = 1.0
        self.pan_start_pos = QPoint(0, 0)
        self.is_panning = False
        self.offset = QPoint(0, 0)
        
        # UI 초기화
        self._init_ui()
        
        # 이벤트 연결
        self._connect_signals()
    
    def _init_ui(self):
        """UI 요소를 초기화합니다."""
        # 레이아웃 설정
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 이미지 라벨 생성 및 설정
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(DARK_BACKGROUND_STYLE)
        
        # 빈 픽스맵으로 초기화
        self.clear()
        
        # 레이아웃에 라벨 추가
        self.layout.addWidget(self.label)
        
        # 마우스 트래킹 활성화
        self.setMouseTracking(True)
        self.label.setMouseTracking(True)
    
    def _connect_signals(self):
        """앱 상태 변경 이벤트에 연결합니다."""
        # 필요한 신호 연결이 있다면 여기에 추가
        pass
    
    def set_pixmap(self, pixmap):
        """
        QPixmap을 설정합니다.
        
        Args:
            pixmap: 표시할 QPixmap 객체
        """
        self.pixmap = pixmap
        self._update_image_scale()
    
    def set_image(self, image):
        """
        NumPy 배열 이미지를 설정합니다.
        
        Args:
            image: NumPy 배열로 된 이미지 (BGR 형식)
        """
        if image is None:
            self.clear()
            return
        
        # NumPy 배열에서 QImage 생성
        height, width, channels = image.shape
        bytes_per_line = channels * width
        
        # BGR -> RGB 변환
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # QImage 생성
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # QPixmap으로 변환하여 설정
        self.set_pixmap(QPixmap.fromImage(q_image))
    
    def clear(self):
        """이미지 뷰를 지웁니다."""
        self.pixmap = QPixmap()
        self.label.setPixmap(self.pixmap)
    
    def reset_zoom(self):
        """확대/축소 수준을 초기화합니다."""
        self.zoom_level = 1.0
        self.offset = QPoint(0, 0)
        self._update_image_scale()
    
    def zoom_in(self):
        """이미지를 확대합니다."""
        if self.zoom_level < self.MAX_ZOOM:
            self.zoom_level *= self.ZOOM_FACTOR
            self._update_image_scale()
    
    def zoom_out(self):
        """이미지를 축소합니다."""
        if self.zoom_level > self.MIN_ZOOM:
            self.zoom_level /= self.ZOOM_FACTOR
            self._update_image_scale()
    
    def toggle_panning(self, enabled):
        """
        패닝 모드를 토글합니다.
        
        Args:
            enabled: 패닝 모드 활성화 여부
        """
        self.is_panning = enabled
        if enabled:
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
    
    def _update_image_scale(self):
        """현재 확대/축소 수준과 오프셋에 따라 이미지를 업데이트합니다."""
        if self.pixmap.isNull():
            self.label.setPixmap(self.pixmap)
            return
        
        # 위젯 크기 얻기
        size = self.label.size()
        
        # 이미지 크기 계산
        scaled_size = self.pixmap.size() * self.zoom_level
        
        # 스케일 변환된 픽스맵 생성
        scaled_pixmap = self.pixmap.scaled(
            scaled_size, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # 이미지가 있는 경우에만 처리
        if not scaled_pixmap.isNull():
            self.label.setPixmap(scaled_pixmap)
            
            # 라벨 중앙에 이미지 배치
            self.label.setAlignment(Qt.AlignCenter)
    
    def wheelEvent(self, event):
        """
        마우스 휠 이벤트 처리 (확대/축소)
        
        Args:
            event: QWheelEvent 객체
        """
        if not self.pixmap.isNull():
            delta = event.angleDelta().y()
            
            # 확대/축소 방향 결정
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
    
    def mousePressEvent(self, event):
        """
        마우스 클릭 이벤트 처리 (패닝 시작)
        
        Args:
            event: QMouseEvent 객체
        """
        if event.button() == Qt.LeftButton and self.is_panning:
            self.pan_start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
    
    def mouseMoveEvent(self, event):
        """
        마우스 이동 이벤트 처리 (패닝)
        
        Args:
            event: QMouseEvent 객체
        """
        if self.is_panning and event.buttons() & Qt.LeftButton:
            # 마우스 위치 변화 계산
            delta = event.pos() - self.pan_start_pos
            self.pan_start_pos = event.pos()
            
            # 오프셋 업데이트
            self.offset += delta
            
            # 이미지 업데이트
            self._update_image_scale()
    
    def mouseReleaseEvent(self, event):
        """
        마우스 버튼 놓음 이벤트 처리 (패닝 종료)
        
        Args:
            event: QMouseEvent 객체
        """
        if event.button() == Qt.LeftButton and self.is_panning:
            self.setCursor(Qt.OpenHandCursor)
    
    def resizeEvent(self, event):
        """
        위젯 크기 변경 이벤트 처리
        
        Args:
            event: QResizeEvent 객체
        """
        super().resizeEvent(event)
        self._update_image_scale()
    
    def contextMenuEvent(self, event):
        """
        컨텍스트 메뉴 이벤트 처리
        
        Args:
            event: QContextMenuEvent 객체
        """
        menu = QMenu(self)
        
        # 메뉴 항목 추가
        zoom_in_action = menu.addAction("확대")
        zoom_out_action = menu.addAction("축소")
        reset_zoom_action = menu.addAction("원래 크기로")
        
        menu.addSeparator()
        
        toggle_pan_action = menu.addAction("패닝 모드 " + ("비활성화" if self.is_panning else "활성화"))
        
        # 메뉴 표시 및 선택 처리
        action = menu.exec_(self.mapToGlobal(event.pos()))
        
        if action == zoom_in_action:
            self.zoom_in()
        elif action == zoom_out_action:
            self.zoom_out()
        elif action == reset_zoom_action:
            self.reset_zoom()
        elif action == toggle_pan_action:
            self.toggle_panning(not self.is_panning) 