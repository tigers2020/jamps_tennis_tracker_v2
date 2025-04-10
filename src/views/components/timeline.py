"""
테니스 공 추적기 애플리케이션의 타임라인 컴포넌트.

비디오 플레이어의 현재 프레임 위치와 총 프레임을 표시하고 조작하는 UI 컴포넌트입니다.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QSlider, QLabel, QHBoxLayout, QVBoxLayout
)

from src.models.app_state import AppState


class Timeline(QWidget):
    """
    비디오 재생 타임라인 UI 컴포넌트.
    
    타임라인 슬라이더와 현재 프레임/총 프레임 표시를 제공합니다.
    사용자는 슬라이더를 드래그하여 비디오의 다른 부분으로 이동할 수 있습니다.
    """
    
    # 사용자가 타임라인에서 위치를 변경할 때 발생하는 신호
    position_changed = Signal(int)
    
    def __init__(self, parent=None):
        """
        Timeline 컴포넌트 초기화
        
        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        
        # AppState 인스턴스 가져오기
        self.app_state = AppState.get_instance()
        
        # 이전 재생 상태 추적을 위한 변수
        self.was_playing = False
        
        # UI 요소 초기화
        self._init_ui()
        
        # 앱 상태 변경 이벤트에 연결
        self._connect_signals()
    
    def _init_ui(self):
        """UI 요소를 초기화합니다."""
        # 메인 레이아웃
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 슬라이더와 프레임 카운터를 위한 수평 레이아웃
        slider_layout = QHBoxLayout()
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.setSpacing(5)
        
        # 타임라인 슬라이더
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.setValue(0)
        self.slider.setTracking(True)
        
        # 슬라이더 이벤트 연결
        self.slider.valueChanged.connect(self.on_slider_value_changed)
        self.slider.sliderPressed.connect(self.on_slider_pressed)
        self.slider.sliderReleased.connect(self.on_slider_released)
        
        # 프레임 카운터 레이아웃
        counter_layout = QHBoxLayout()
        counter_layout.setContentsMargins(0, 0, 0, 0)
        counter_layout.setSpacing(0)
        
        # 현재 프레임 라벨
        self.current_frame_label = QLabel("1")
        self.current_frame_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.current_frame_label.setMinimumWidth(30)
        
        # 총 프레임 라벨
        self.total_frames_label = QLabel("/ 0")
        self.total_frames_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 레이아웃에 위젯 추가
        counter_layout.addWidget(self.current_frame_label)
        counter_layout.addWidget(self.total_frames_label)
        
        slider_layout.addWidget(self.slider, 1)  # 1은 스트레치 팩터입니다
        slider_layout.addLayout(counter_layout)
        
        layout.addLayout(slider_layout)
        
        # 고정 높이 설정
        self.setFixedHeight(30)
    
    def _connect_signals(self):
        """앱 상태 변경 이벤트에 연결합니다."""
        # 현재 프레임이 변경될 때
        self.app_state.frame_changed.connect(self.on_frame_changed)
        
        # 총 프레임이 변경될 때
        self.app_state.total_frames_changed.connect(self.on_total_frames_changed)
    
    def set_frame_count(self, count):
        """
        총 프레임 수를 설정합니다.
        
        Args:
            count: 총 프레임 수
        """
        # 슬라이더 최대값 설정 (0-based)
        self.slider.setMaximum(max(0, count - 1))
        
        # 총 프레임 라벨 업데이트
        self.total_frames_label.setText(f"/ {count}")
    
    def set_current_frame(self, frame):
        """
        현재 프레임을 설정합니다.
        
        Args:
            frame: 현재 프레임 인덱스 (0-based)
        """
        # 범위 내에 있는지 확인하고 슬라이더 값 설정
        self.slider.setValue(max(0, min(frame, self.slider.maximum())))
        
        # 현재 프레임 라벨 업데이트 (1-based 표시)
        self.current_frame_label.setText(str(frame + 1))
    
    def on_slider_value_changed(self, value):
        """
        슬라이더 값이 변경될 때 호출됩니다.
        
        Args:
            value: 새 슬라이더 값 (현재 프레임)
        """
        # 현재 프레임 라벨 업데이트 (1-based 표시)
        self.current_frame_label.setText(str(value + 1))
        
        # 위치 변경 신호 발생
        self.position_changed.emit(value)
    
    def on_slider_pressed(self):
        """슬라이더가 눌렸을 때 호출됩니다."""
        # 현재 재생 상태 저장
        self.was_playing = (self.app_state.playback_state == 'play')
        
        # 재생 중이었다면 일시 정지
        if self.was_playing:
            self.app_state.set_playback_state('pause')
    
    def on_slider_released(self):
        """슬라이더가 놓아졌을 때 호출됩니다."""
        # 이전에 재생 중이었다면 다시 재생
        if self.was_playing:
            self.app_state.set_playback_state('play')
            self.was_playing = False
    
    def on_frame_changed(self, frame):
        """
        앱 상태의 현재 프레임이 변경될 때 호출됩니다.
        
        Args:
            frame: 새 현재 프레임
        """
        # 현재 프레임 설정
        self.set_current_frame(frame)
    
    def on_total_frames_changed(self, count):
        """
        앱 상태의 총 프레임이 변경될 때 호출됩니다.
        
        Args:
            count: 새 총 프레임 수
        """
        # 총 프레임 수 설정
        self.set_frame_count(count)
    
    def update_from_app_state(self):
        """앱 상태에서 타임라인 UI를 업데이트합니다."""
        # 총 프레임 수 설정
        self.set_frame_count(self.app_state.total_frames)
        
        # 현재 프레임 설정
        self.set_current_frame(self.app_state.current_frame)
    
    def reset(self):
        """타임라인을 초기 상태로 리셋합니다."""
        # 슬라이더 초기화
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.setValue(0)
        
        # 라벨 초기화
        self.current_frame_label.setText("1")
        self.total_frames_label.setText("/ 0") 