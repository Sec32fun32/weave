import * as globals from '@wandb/weave/common/css/globals.styles';
import * as _ from 'lodash';
import React, {useCallback, useState} from 'react';
import styled, {css} from 'styled-components';

import {IconButton} from '../IconButton';
import {getPanelStacksForType} from '../Panel2/availablePanels';
import {ChildPanelConfig, ChildPanelFullConfig} from '../Panel2/ChildPanel';
import {
  IconCaret as IconCaretUnstyled,
  IconOverflowHorizontal as IconOverflowHorizontalUnstyled,
  IconWeave as IconWeaveUnstyled,
} from '../Panel2/Icons';
import {panelChildren} from '../Panel2/panelTree';
import {OutlineItemPopupMenu} from './OutlineItemPopupMenu';

const OutlineContainer = styled.div`
  padding: 8px 0;
`;
OutlineContainer.displayName = 'OutlineContainer';

const OutlineItem = styled.div``;
OutlineItem.displayName = 'OutlineItem';

const OutlineItemMenuButton = styled(IconButton).attrs({small: true})`
  flex-shrink: 0;
  margin: 0 8px 0 4px;
`;
OutlineItemMenuButton.displayName = 'OutlineItemMenuButton';

const OutlineItemTitle = styled.div<{level: number}>`
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
  padding-top: 4px;
  padding-bottom: 4px;
  padding-left: ${p => p.level * 11 + 8}px;
  line-height: 130%;

  &:hover {
    background-color: ${globals.GRAY_50};
  }

  &:not(:hover) ${OutlineItemMenuButton} {
    visibility: hidden;
  }
`;
OutlineItemTitle.displayName = 'OutlineItemTitle';

const OutlineItemToggle = styled.div<{expanded: boolean}>`
  flex-shrink: 0;
  display: flex;
  width: 18px;
  margin-right: 4px;
  cursor: pointer;
  transform: rotate(${p => (p.expanded ? 0 : -90)}deg);

  color: ${globals.GRAY_500};
  &:hover {
    color: ${globals.GRAY_600};
    background-color: ${globals.GRAY_50};
  }
`;
OutlineItemToggle.displayName = 'OutlineItemToggle';

const OutlineItemIcon = styled.div`
  flex-shrink: 0;
  display: flex;
  margin-right: 8px;
`;
OutlineItemIcon.displayName = 'OutlineItemIcon';

const OutlineItemName = styled.div`
  flex-shrink: 0;
  max-width: 100px;
  overflow-wrap: break-word;
`;
OutlineItemName.displayName = 'OutlineItemName';

const OutlineItemPanelID = styled.div`
  color: ${globals.GRAY_500};
  font-size: 15px;
  font-family: 'Inconsolata', monospace;
  margin-left: 10px;
  flex-grow: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;
OutlineItemPanelID.displayName = 'OutlineItemPanelID';

const iconStyles = css`
  height: 18px;
  width: 18px;
`;

const IconCaret = styled(IconCaretUnstyled)`
  ${iconStyles}
`;
IconCaret.displayName = 'IconCaret';

const IconOverflowHorizontal = styled(IconOverflowHorizontalUnstyled)`
  ${iconStyles}
`;
IconOverflowHorizontal.displayName = 'IconOverflowHorizontal';

const IconWeave = styled(IconWeaveUnstyled)`
  ${iconStyles}
`;
IconWeave.displayName = 'IconWeave';

export type OutlinePanelProps = OutlineProps & {
  name: string;
  localConfig: ChildPanelFullConfig;
  path: string[];
  level?: number;
};

const OutlinePanel: React.FC<OutlinePanelProps> = props => {
  const {
    name,
    localConfig,
    selected,
    setSelected,
    path,
    config,
    updateConfig,
    updateConfig2,
    level = 0,
    setInspectingRoot,
  } = props;
  const curPanelId = getPanelStacksForType(
    localConfig?.input_node?.type ?? 'invalid',
    localConfig?.id
  ).curPanelId;
  const children = panelChildren(localConfig); // TODO: curPanelId!

  const [expanded, setExpanded] = useState(true);

  const toggleExpanded = useCallback(() => {
    if (children != null) {
      setExpanded(prev => !prev);
    }
  }, [children]);

  return (
    <OutlineItem>
      <OutlineItemTitle
        level={level}
        onClick={() => {
          const isRoot = _.isEqual(path, []);
          isRoot ? setInspectingRoot(true) : setSelected(path);
        }}>
        <OutlineItemToggle
          expanded={expanded}
          onClick={e => {
            e.stopPropagation();
            toggleExpanded();
          }}>
          {children != null && <IconCaret />}
        </OutlineItemToggle>
        <OutlineItemIcon>
          <IconWeave />
        </OutlineItemIcon>

        <OutlineItemName>{name}</OutlineItemName>
        <OutlineItemPanelID>{curPanelId}</OutlineItemPanelID>
        {path.length > 0 && (
          <OutlineItemPopupMenu
            config={config}
            localConfig={localConfig}
            path={path}
            updateConfig={updateConfig}
            updateConfig2={updateConfig2}
            trigger={
              <OutlineItemMenuButton onClick={e => e.stopPropagation()}>
                <IconOverflowHorizontal />
              </OutlineItemMenuButton>
            }
          />
        )}
      </OutlineItemTitle>
      {expanded &&
        children != null &&
        _.map(children, (conf, key) => (
          <OutlinePanel
            key={key}
            name={key}
            // root config is passed all the way down so we can operate on the whole thing
            config={props.config}
            localConfig={conf}
            updateConfig={props.updateConfig}
            updateConfig2={props.updateConfig2}
            selected={selected}
            setSelected={setSelected}
            path={[...path, key]}
            level={level + 1}
            setInspectingRoot={setInspectingRoot}
          />
        ))}
    </OutlineItem>
  );
};

export interface OutlineProps {
  config: ChildPanelFullConfig;
  updateConfig: (newConfig: ChildPanelFullConfig) => void;
  updateConfig2: (
    change: (oldConfig: ChildPanelConfig) => ChildPanelFullConfig
  ) => void;
  selected: string[];
  setSelected: (path: string[]) => void;
  setInspectingRoot: (inspectingRoot: boolean) => void;
}

export const Outline: React.FC<OutlineProps> = props => {
  return (
    <OutlineContainer>
      <OutlinePanel
        name="root"
        // root config is passed all the way down so we can operate on the whole thing
        config={props.config}
        updateConfig={props.updateConfig}
        updateConfig2={props.updateConfig2}
        localConfig={props.config}
        selected={props.selected}
        setSelected={props.setSelected}
        path={[]}
        setInspectingRoot={props.setInspectingRoot}
      />
    </OutlineContainer>
  );
};
