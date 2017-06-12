import Inferno from 'inferno';
import FilterDropdown from '../FilterDropdown';

import ChalProgress from '../ChalProgress';

import './ChalToolbar.scss';

export default props =>
  <div className="chal-toolbar">
    <FilterDropdown
      title="Categories"
      options={props.categories}
      filters={props.categoryFilters}
      onFilter={props.onUpdateCategoryFilters}
      position="left"
      multi
    />
    <ChalProgress total={props.totalPoints} completed={props.solvedPoints} loading={props.progressLoading} />
    <FilterDropdown
      title="Filter"
      options={props.completedOptions}
      filters={props.completedFilters}
      onFilter={props.onUpdateCompletedFilters}
      position="right"
      multi
    />
    <FilterDropdown
      title="Sort"
      options={[{ label: 'Points DESC', value: 'points_desc' }, { label: 'Points ASC', value: 'points_asc' }]}
      position="right"
    />
  </div>;
