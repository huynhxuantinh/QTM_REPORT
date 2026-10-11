import React, { useState } from 'react';
import { useDevices } from '@/features/devices/hooks/useDevices';
import { reportService, ReportFilterParams } from '@/features/reports/services/reportService';
import { triggerBlobDownload } from '@/utils/download';
import { HealthStatus } from '@/types/health';
import { FileText, Filter, Calendar, FileSpreadsheet, Loader2 } from 'lucide-react';
import { getErrorMessage } from '@/utils/i18n';
import { useNotifications } from '@/context/useNotifications';
import { ErrorState } from '@/components/common/ErrorState';

export const ReportsPage: React.FC = () => {
  const { success, error: notifyError } = useNotifications();
  const { data: pageData, isError: isDevicesError, error: devicesError, refetch: refetchDevices } = useDevices();
  const devices = pageData?.items || [];

  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>('');
  const [selectedSite, setSelectedSite] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');

  const [isDownloadingExcel, setIsDownloadingExcel] = useState(false);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);

  const uniqueSites = Array.from(new Set(devices.map((d) => d.site).filter(Boolean))) as string[];

  if (isDevicesError) {
    return (
      <ErrorState
        title="Không thể tải dữ liệu tạo báo cáo"
        message={getErrorMessage(devicesError)}
        onRetry={() => refetchDevices()}
      />
    );
  }

  const buildFilters = (): ReportFilterParams => {
    const filters: ReportFilterParams = {};
    if (dateFrom) filters.date_from = new Date(`${dateFrom}T00:00:00+07:00`).toISOString();
    if (dateTo) filters.date_to = new Date(`${dateTo}T23:59:59.999+07:00`).toISOString();
    if (selectedDeviceId) filters.device_id = parseInt(selectedDeviceId, 10);
    if (selectedSite) filters.site = selectedSite;
    if (selectedStatus) filters.status = selectedStatus as HealthStatus;
    return filters;
  };

  const handleDownloadExcel = async () => {
    setIsDownloadingExcel(true);
    try {
      const filters = buildFilters();
      const blob = await reportService.downloadXlsx(filters);
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      triggerBlobDownload(blob, `network-health-report-${timestamp}.xlsx`);
      success('Đã tải báo cáo Excel', 'Tệp Excel đã được lưu vào thư mục tải xuống của trình duyệt.');
    } catch (error: unknown) {
      notifyError('Không thể tạo báo cáo Excel', getErrorMessage(error));
    } finally {
      setIsDownloadingExcel(false);
    }
  };

  const handleDownloadPdf = async () => {
    setIsDownloadingPdf(true);
    try {
      const filters = buildFilters();
      const blob = await reportService.downloadPdf(filters);
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      triggerBlobDownload(blob, `network-health-report-${timestamp}.pdf`);
      success('Đã tải báo cáo PDF', 'Tệp báo cáo đã được lưu vào thư mục tải xuống của trình duyệt.');
    } catch (error: unknown) {
      notifyError('Không thể tạo báo cáo PDF', getErrorMessage(error));
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  return (
    <div className="fade-in">
      <div className="mb-4">
        <h4 className="fw-bold text-dark mb-1">Xuất Báo cáo Giám sát</h4>
        <p className="text-muted small mb-0">
          Tạo và tải về báo cáo tổng hợp sức khỏe router theo thời gian dưới định dạng CSV và PDF
        </p>
      </div>

      <div className="row g-4">
        {/* Filters Card */}
        <div className="col-12 col-lg-8">
          <div className="card shadow-sm border-0 rounded-3">
            <div className="card-header bg-white border-0 pt-3 pb-2 d-flex align-items-center gap-2">
              <Filter size={18} className="text-primary" />
              <h6 className="fw-bold text-dark mb-0">Tiêu chí lọc dữ liệu báo cáo</h6>
            </div>

            <div className="card-body p-4">
              <div className="row g-3">
                <div className="col-12 col-md-6">
                  <label className="form-label small fw-semibold text-muted">Từ ngày</label>
                  <div className="input-group">
                    <span className="input-group-text bg-light border-end-0 text-muted">
                      <Calendar size={16} />
                    </span>
                    <input
                      type="date"
                      className="form-control border-start-0 ps-0 small"
                      value={dateFrom}
                      onChange={(e) => setDateFrom(e.target.value)}
                    />
                  </div>
                </div>

                <div className="col-12 col-md-6">
                  <label className="form-label small fw-semibold text-muted">Đến ngày</label>
                  <div className="input-group">
                    <span className="input-group-text bg-light border-end-0 text-muted">
                      <Calendar size={16} />
                    </span>
                    <input
                      type="date"
                      className="form-control border-start-0 ps-0 small"
                      value={dateTo}
                      onChange={(e) => setDateTo(e.target.value)}
                    />
                  </div>
                </div>

                <div className="col-12">
                  <div className="alert alert-info py-2 px-3 mb-0 small" role="note">
                    Thời gian trong báo cáo được hiển thị theo giờ Việt Nam (GMT+7). Nếu không chọn ngày, hệ thống sẽ xuất toàn bộ lịch sử.
                  </div>
                </div>

                <div className="col-12 col-md-4">
                  <label className="form-label small fw-semibold text-muted">Thiết bị cụ thể</label>
                  <select
                    className="form-select small"
                    value={selectedDeviceId}
                    onChange={(e) => setSelectedDeviceId(e.target.value)}
                  >
                    <option value="">Tất cả thiết bị</option>
                    {devices.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name} ({d.host})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-12 col-md-4">
                  <label className="form-label small fw-semibold text-muted">Khu vực / Chi nhánh</label>
                  <select
                    className="form-select small"
                    value={selectedSite}
                    onChange={(e) => setSelectedSite(e.target.value)}
                  >
                    <option value="">Tất cả khu vực</option>
                    {uniqueSites.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-12 col-md-4">
                  <label className="form-label small fw-semibold text-muted">Trạng thái tổng hợp</label>
                  <select
                    className="form-select small"
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                  >
                    <option value="">Tất cả trạng thái</option>
                    <option value="Healthy">Chỉ hoạt động tốt</option>
                    <option value="Warning">Chỉ cảnh báo</option>
                    <option value="Critical">Chỉ nghiêm trọng</option>
                  </select>
                </div>
              </div>

              <hr className="my-4" />

              <div className="d-flex flex-wrap gap-3">
                <button
                  className="btn btn-success d-flex align-items-center gap-2 px-4 shadow-sm"
                  onClick={handleDownloadExcel}
                  disabled={isDownloadingExcel || isDownloadingPdf}
                >
                  {isDownloadingExcel ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      <span>Đang xuất Excel...</span>
                    </>
                  ) : (
                    <>
                      <FileSpreadsheet size={18} />
                      <span className="fw-semibold">Tải báo cáo Excel (.xlsx)</span>
                    </>
                  )}
                </button>

                <button
                  className="btn btn-danger d-flex align-items-center gap-2 px-4 shadow-sm"
                  onClick={handleDownloadPdf}
                  disabled={isDownloadingExcel || isDownloadingPdf}
                >
                  {isDownloadingPdf ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      <span>Đang xuất PDF...</span>
                    </>
                  ) : (
                    <>
                      <FileText size={18} />
                      <span className="fw-semibold">Tải báo cáo PDF</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Info & Specifications Card */}
        <div className="col-12 col-lg-4">
          <div className="card shadow-sm border-0 rounded-3 mb-3">
            <div className="card-header bg-white border-0 pt-3 pb-2">
              <h6 className="fw-bold text-dark mb-0">Quy cách định dạng</h6>
            </div>
            <div className="card-body p-3 text-muted small">
              <div className="mb-3">
                <strong className="text-dark d-block mb-1">1. Định dạng Excel (.xlsx)</strong>
                <p className="mb-0">
                  Gồm 4 sheet: tổng quan, lịch sử kiểm tra, cổng mạng và cảnh báo; có bộ lọc, màu trạng thái và biểu đồ.
                </p>
              </div>

              <div className="mb-3">
                <strong className="text-dark d-block mb-1">2. Định dạng PDF</strong>
                <p className="mb-0">
                  Có tổng quan, thống kê theo router, chi tiết từng lần quét, trạng thái cổng mới nhất, cảnh báo và số trang.
                </p>
              </div>

              <div>
                <strong className="text-dark d-block mb-1">3. Bảo mật thông tin</strong>
                <p className="mb-0">
                  Không chứa mật khẩu, mã bí mật hay kết quả lệnh riêng tư dạng thô trong tệp báo cáo.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
