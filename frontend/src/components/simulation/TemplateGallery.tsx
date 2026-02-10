import React from 'react';
import { useTranslation } from 'react-i18next';

interface Template {
  id: number;
  name: string;
  description?: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  rule_conditions: any;
  sample_test_data: any;
  expected_results?: any;
}

interface TemplateGalleryProps {
  templates: Template[];
  onSelectTemplate: (template: Template) => void;
  onClose: () => void;
}

export const TemplateGallery: React.FC<TemplateGalleryProps> = ({
  templates,
  onSelectTemplate,
  onClose,
}) => {
  const { t } = useTranslation();

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyIcon = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return '⭐';
      case 'medium':
        return '⭐⭐';
      case 'hard':
        return '⭐⭐⭐';
      default:
        return '';
    }
  };

  // Group templates by category
  const groupedTemplates = templates.reduce((acc, template) => {
    const category = template.category || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(template);
    return acc;
  }, {} as Record<string, Template[]>);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-bold">{t('simulation.templates.title', '시뮬레이션 템플릿')}</h2>
              <p className="text-gray-600 mt-2">
                {t('simulation.templates.subtitle', '미리 구성된 시뮬레이션 템플릿을 선택하세요')}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Templates by Category */}
          {Object.entries(groupedTemplates).map(([category, categoryTemplates]) => (
            <div key={category} className="mb-8">
              <h3 className="text-lg font-semibold mb-4 text-gray-700">
                {t(`simulation.templates.category.${category}`, category)}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {categoryTemplates.map((template) => (
                  <div
                    key={template.id}
                    className="border rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer bg-white"
                    onClick={() => onSelectTemplate(template)}
                  >
                    {/* Template Header */}
                    <div className="flex justify-between items-start mb-3">
                      <h4 className="font-semibold text-lg flex-1">{template.name}</h4>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(template.difficulty)}`}>
                        {getDifficultyIcon(template.difficulty)}
                      </span>
                    </div>

                    {/* Description */}
                    {template.description && (
                      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                        {template.description}
                      </p>
                    )}

                    {/* Category Badge */}
                    <div className="flex items-center justify-between">
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {t(`simulation.templates.category.${template.category}`, template.category)}
                      </span>
                      <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                        {t('simulation.templates.use', '사용하기')} →
                      </button>
                    </div>

                    {/* Expected Results Preview */}
                    {template.expected_results && (
                      <div className="mt-3 pt-3 border-t">
                        <p className="text-xs text-gray-500 mb-2">
                          {t('simulation.templates.expectedResults', '예상 결과')}
                        </p>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          {template.expected_results.match_rate && (
                            <div>
                              <span className="text-gray-600">{t('simulation.metrics.matchRate', '매칭률')}:</span>
                              <span className="font-semibold ml-1">
                                {template.expected_results.match_rate}%
                              </span>
                            </div>
                          )}
                          {template.expected_results.avg_response_time_ms && (
                            <div>
                              <span className="text-gray-600">{t('simulation.metrics.avgTime', '평균 시간')}:</span>
                              <span className="font-semibold ml-1">
                                {template.expected_results.avg_response_time_ms}ms
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Empty State */}
          {Object.keys(groupedTemplates).length === 0 && (
            <div className="text-center py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                {t('simulation.templates.noTemplates', '템플릿이 없습니다')}
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                {t('simulation.templates.noTemplatesDesc', '사용 가능한 시뮬레이션 템플릿이 없습니다')}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TemplateGallery;
