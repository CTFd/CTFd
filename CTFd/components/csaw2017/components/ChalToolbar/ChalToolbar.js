import Inferno from 'inferno';
import FilterDropdown from '../FilterDropdown';

import ChalProgress from '../ChalProgress';

import './ChalToolbar.scss';

export default props =>
  <div className="chal-toolbar">
    <FilterDropdown
      title="Categories"
      options={['All', 'Apple', 'Banana', 'Carrot', 'Donut', 'Eclair', 'Froyo']}
      position="left"
    />
    <ChalProgress />
    <FilterDropdown title="Filter" options={['All', 'Completed', 'Not Completed']} position="right" />
    <FilterDropdown title="Sort" options={['Points DESC', 'Points ASC']} position="right" />
  </div>;
