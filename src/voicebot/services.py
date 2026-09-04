from voicebot.analysis import AnalysisPipeline
from voicebot.artifacts import ArtifactManager
from voicebot.config import Settings
from voicebot.evaluation import ConversationEvaluator
from voicebot.recordings import RecordingDownloader
from voicebot.transcription import RecordingTranscriber


def build_analysis_pipeline(settings: Settings) -> AnalysisPipeline:
    artifacts = ArtifactManager(settings.calls_directory)
    return AnalysisPipeline(
        artifacts,
        RecordingDownloader(settings),
        RecordingTranscriber(settings),
        ConversationEvaluator(settings),
    )
