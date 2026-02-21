import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Play, 
  BarChart3, 
  ToggleLeft, 
  ToggleRight,
  MoreVertical,
  Clock,
  CheckCircle,
  XCircle,
  Brain
} from 'lucide-react';
import { DispatchRulesAPI, DispatchRule, CreateRulePayload } from '../api/dispatch-rules';

const DispatchRulesPage: React.FC = () => {
  const [rules, setRules] = useState<DispatchRule[]>([]);
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedRule, setSelectedRule] = useState<DispatchRule | null>(null);
  const [notification, setNotification] = useState({ show: false, message: '', type: 'success' as 'success' | 'error' });
  
  const [formData, setFormData] = useState<CreateRulePayload>({
    name: '',
    description: '',
    rule_type: 'assignment',
    priority: 50,
    conditions: {},
    actions: {}
  });

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    setLoading(true);
    try {
      const data = await DispatchRulesAPI.list();
      setRules(data);
    } catch (error) {
      showNotification('Failed to load rules', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await DispatchRulesAPI.create(formData);
      showNotification('Rule created successfully', 'success');
      setOpenDialog(false);
      loadRules();
      resetForm();
    } catch (error) {
      showNotification('Failed to create rule', 'error');
    }
  };

  const handleToggle = async (ruleId: number, isActive: boolean) => {
    try {
      if (isActive) {
        await DispatchRulesAPI.deactivate(ruleId);
      } else {
        await DispatchRulesAPI.activate(ruleId);
      }
      showNotification(`Rule ${isActive ? 'deactivated' : 'activated'}`, 'success');
      loadRules();
    } catch (error) {
      showNotification('Failed to toggle rule', 'error');
    }
  };

  const handleDelete = async (ruleId: number) => {
    if (window.confirm('Are you sure you want to delete this rule?')) {
      try {
        await DispatchRulesAPI.delete(ruleId);
        showNotification('Rule deleted', 'success');
        loadRules();
      } catch (error) {
        showNotification('Failed to delete rule', 'error');
      }
    }
  };

  const showNotification = (message: string, type: 'success' | 'error') => {
    setNotification({ show: true, message, type });
    setTimeout(() => setNotification({ show: false, message: '', type: 'success' }), 3000);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      rule_type: 'assignment',
      priority: 50,
      conditions: {},
      actions: {}
    });
  };

  const getRuleTypeColor = (type: string) => {
    switch (type) {
      case 'assignment': return 'bg-blue-100 text-blue-800';
      case 'constraint': return 'bg-yellow-100 text-yellow-800';
      case 'optimization': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRuleTypeIcon = (type: string) => {
    switch (type) {
      case 'assignment': return <CheckCircle className="w-4 h-4" />;
      case 'constraint': return <XCircle className="w-4 h-4" />;
      case 'optimization': return <Brain className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <Layout>
        <Loading />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">규칙 관리</h1>
            <p className="text-gray-600 mt-1">배차 규칙을 생성하고 관리합니다</p>
          </div>
          <Button
            onClick={() => setOpenDialog(true)}
            className="flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>규칙 생성</span>
          </Button>
        </div>

        {/* Notification */}
        {notification.show && (
          <div className={`mb-4 p-4 rounded-lg ${
            notification.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
          }`}>
            {notification.message}
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">전체 규칙</p>
                <p className="text-2xl font-bold text-gray-900">{rules.length}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">활성 규칙</p>
                <p className="text-2xl font-bold text-green-600">
                  {rules.filter(r => r.is_active).length}
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">비활성 규칙</p>
                <p className="text-2xl font-bold text-gray-600">
                  {rules.filter(r => !r.is_active).length}
                </p>
              </div>
              <div className="p-3 bg-gray-100 rounded-lg">
                <XCircle className="w-6 h-6 text-gray-600" />
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">평균 성공률</p>
                <p className="text-2xl font-bold text-blue-600">
                  {rules.length > 0 
                    ? Math.round(rules.reduce((acc, r) => acc + (r.success_rate || 0), 0) / rules.length * 100)
                    : 0}%
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-lg">
                <Brain className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </Card>
        </div>

        {/* Rules Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {rules.map((rule) => (
            <Card key={rule.id} className="p-6 hover:shadow-lg transition-shadow">
              {/* Header */}
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{rule.name}</h3>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {rule.description || '설명 없음'}
                  </p>
                </div>
                <button
                  onClick={() => handleToggle(rule.id, rule.is_active)}
                  className="ml-2"
                >
                  {rule.is_active ? (
                    <ToggleRight className="w-8 h-8 text-green-600" />
                  ) : (
                    <ToggleLeft className="w-8 h-8 text-gray-400" />
                  )}
                </button>
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-2 mb-4">
                <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium ${getRuleTypeColor(rule.rule_type)}`}>
                  {getRuleTypeIcon(rule.rule_type)}
                  <span>{rule.rule_type}</span>
                </span>
                <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
                  우선순위: {rule.priority}
                </span>
                <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                  v{rule.version}
                </span>
              </div>

              {/* Stats */}
              <div className="border-t border-gray-200 pt-4 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">실행 횟수</span>
                  <span className="font-semibold text-gray-900">{rule.execution_count || 0}</span>
                </div>
                <div className="flex justify-between text-sm mt-2">
                  <span className="text-gray-600">성공률</span>
                  <span className="font-semibold text-green-600">
                    {((rule.success_rate || 0) * 100).toFixed(1)}%
                  </span>
                </div>
                {rule.avg_execution_time_ms && (
                  <div className="flex justify-between text-sm mt-2">
                    <span className="text-gray-600">평균 실행 시간</span>
                    <span className="font-semibold text-blue-600">
                      {rule.avg_execution_time_ms.toFixed(1)}ms
                    </span>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex space-x-2">
                <button
                  className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium flex items-center justify-center space-x-1"
                  onClick={() => {/* TODO: Test rule */}}
                >
                  <Play className="w-4 h-4" />
                  <span>테스트</span>
                </button>
                <button
                  className="flex-1 px-3 py-2 bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100 transition-colors text-sm font-medium flex items-center justify-center space-x-1"
                  onClick={() => {/* TODO: View stats */}}
                >
                  <BarChart3 className="w-4 h-4" />
                  <span>통계</span>
                </button>
                <button
                  className="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
                  onClick={() => handleDelete(rule.id)}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </Card>
          ))}
        </div>

        {/* Empty State */}
        {rules.length === 0 && (
          <Card className="p-12 text-center">
            <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">규칙이 없습니다</h3>
            <p className="text-gray-600 mb-6">첫 번째 배차 규칙을 생성해보세요</p>
            <Button onClick={() => setOpenDialog(true)}>
              <Plus className="w-5 h-5 mr-2" />
              규칙 생성
            </Button>
          </Card>
        )}

        {/* Create Rule Modal */}
        {openDialog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">새 규칙 생성</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    규칙 이름
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="예: 냉동 주문 → 냉동탑차 배정"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    설명
                  </label>
                  <textarea
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="규칙에 대한 설명을 입력하세요"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      규칙 타입
                    </label>
                    <select
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      value={formData.rule_type}
                      onChange={(e) => setFormData({ ...formData, rule_type: e.target.value as any })}
                    >
                      <option value="assignment">Assignment (배정)</option>
                      <option value="constraint">Constraint (제약)</option>
                      <option value="optimization">Optimization (최적화)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      우선순위 (1-100)
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      value={formData.priority}
                      onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    조건 (JSON)
                  </label>
                  <textarea
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                    rows={5}
                    value={JSON.stringify(formData.conditions, null, 2)}
                    onChange={(e) => {
                      try {
                        setFormData({ ...formData, conditions: JSON.parse(e.target.value) });
                      } catch {}
                    }}
                    placeholder='{"order.temperature_zone": "냉동"}'
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    액션 (JSON)
                  </label>
                  <textarea
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                    rows={5}
                    value={JSON.stringify(formData.actions, null, 2)}
                    onChange={(e) => {
                      try {
                        setFormData({ ...formData, actions: JSON.parse(e.target.value) });
                      } catch {}
                    }}
                    placeholder='{"prefer_vehicle_type": "냉동탑차"}'
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  onClick={() => {
                    setOpenDialog(false);
                    resetForm();
                  }}
                >
                  취소
                </button>
                <Button onClick={handleCreate}>
                  생성
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default DispatchRulesPage;
